# reports/views.py
from datetime import timedelta, date, datetime
import json
import numpy as np
import pandas as pd
from collections import defaultdict

from django.db.models import Sum, Case, When, IntegerField, F, Value, FloatField, Q
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone

from inventory.models import Medicine, Transaction, Manufacturer

# ---- field names in your schema ----
TXN_DATE_FIELD   = "created_at"       # DateTimeField
TXN_TYPE_FIELD   = "ttype"            # values: BOUGHT/SOLD (+ maybe IMPORT/EXPORT)
QTY_FIELD        = "quantity"
PRICE_FIELD      = "unit_price"
MEDICINE_FK      = "medicine"         # FK to Medicine
EXPIRY_FIELD     = "exp_date"         # on Medicine
COST_FIELD       = "cost_price"       # on Medicine
ON_HAND_FIELD    = "quantity_on_hand" # on Medicine

def reports_view(request):
    user = request.user
    today = timezone.localdate()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)
    
    # Get date range from request (for filtering)
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    report_type = request.GET.get('report_type', 'overview')  # overview, sales, inventory, profit

    # --------- Query once, then use Pandas ----------
    txns_qs = (
        Transaction.objects
        .filter(owner=user)
        .select_related(MEDICINE_FK)
        .values(
            TXN_DATE_FIELD, TXN_TYPE_FIELD, QTY_FIELD, PRICE_FIELD,
            f"{MEDICINE_FK}__name"
        )
    )
    txns = list(txns_qs)
    df = pd.DataFrame(txns) if txns else pd.DataFrame(
        columns=[TXN_DATE_FIELD, TXN_TYPE_FIELD, QTY_FIELD, PRICE_FIELD, f"{MEDICINE_FK}__name"]
    )

    # Normalize datatypes
    if not df.empty:
        # datetimes -> date, and helper columns
        df[TXN_DATE_FIELD] = pd.to_datetime(df[TXN_DATE_FIELD])
        df["date_only"] = df[TXN_DATE_FIELD].dt.date
        df["type_u"] = df[TXN_TYPE_FIELD].astype(str).str.upper()
        df["is_sold"]   = df["type_u"].isin(["SOLD", "EXPORT"])
        df["is_bought"] = df["type_u"].isin(["BOUGHT", "IMPORT"])
        df["amount"] = df[QTY_FIELD].fillna(0).astype(float) * df[PRICE_FIELD].fillna(0).astype(float)
        df["med_name"] = df[f"{MEDICINE_FK}__name"].fillna("—")
        # week key
        iso = df[TXN_DATE_FIELD].dt.isocalendar()
        df["week_key"] = iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)

    # --------- Cards (revenue & stats) --------------
    rev_day = rev_week = rev_month = rev_year = 0.0
    total_transactions = len(df)
    units_sold = 0

    if not df.empty:
        # date filters
        day_mask   = df["date_only"].eq(today)
        week_mask  = df["date_only"].between(start_of_week, today)
        month_mask = df["date_only"].between(start_of_month, today)
        year_mask  = df[TXN_DATE_FIELD].dt.year.eq(today.year)

        sold_mask = df["is_sold"]

        rev_day   = float((df.loc[sold_mask & day_mask,   "amount"]).sum())
        rev_week  = float((df.loc[sold_mask & week_mask,  "amount"]).sum())
        rev_month = float((df.loc[sold_mask & month_mask, "amount"]).sum())
        rev_year  = float((df.loc[sold_mask & year_mask,  "amount"]).sum())
        units_sold = int((df.loc[sold_mask, QTY_FIELD]).sum())

    sold_orders_count = int(df["is_sold"].sum()) if not df.empty else 0
    avg_order_value = (rev_month / sold_orders_count) if sold_orders_count else 0.0

    # --------- Revenue timeseries (last 60 days) ----
    days_back = 60
    start_ts = today - timedelta(days=days_back - 1)
    ts_dates = pd.date_range(start_ts, periods=days_back, freq="D").date
    ts_series = pd.Series(0.0, index=pd.Index(ts_dates, name="date_only"))

    if not df.empty:
        rev_by_day = df.loc[df["is_sold"]].groupby("date_only")["amount"].sum()
        ts_series = ts_series.add(rev_by_day, fill_value=0.0)

    revenue_timeseries = [{"date": d.isoformat(), "revenue": float(v)} for d, v in ts_series.items()]

    # --------- Top medicines by qty sold ------------
    top_medicines = []
    if not df.empty:
        g = df.loc[df["is_sold"]].groupby("med_name")[QTY_FIELD].sum().sort_values(ascending=False).head(10)
        top_medicines = [{"name": n, "qty_sold": int(q)} for n, q in g.items()]

    # --------- Expiry buckets (from Medicine table) -
    meds_qs = Medicine.objects.filter(owner=user).values("name", EXPIRY_FIELD, ON_HAND_FIELD, COST_FIELD)
    meds = list(meds_qs)
    df_meds = pd.DataFrame(meds) if meds else pd.DataFrame(columns=["name", EXPIRY_FIELD, ON_HAND_FIELD, COST_FIELD])

    expired = expiring_30d = ok = 0
    if not df_meds.empty:
        df_meds[EXPIRY_FIELD] = pd.to_datetime(df_meds[EXPIRY_FIELD]).dt.date
        expired      = int((df_meds[EXPIRY_FIELD] < today).sum())
        expiring_30d = int(((df_meds[EXPIRY_FIELD] >= today) & (df_meds[EXPIRY_FIELD] <= today + timedelta(days=30))).sum())
        ok           = int((df_meds[EXPIRY_FIELD] >  today + timedelta(days=30)).sum())
    expiry_pie = {"expired": expired, "expiring_30d": expiring_30d, "ok": ok}

    # --------- Weekly bought vs sold ----------------
        # ---- weekly bought vs sold (last 12 weeks) ----
    weekly_bought_sold = []
    if not df.empty:
        df["week_key"] = df["week_key"].astype(str)

        # sum quantities, not counts
        df_b = df.loc[df["is_bought"], ["week_key", QTY_FIELD]]
        df_s = df.loc[df["is_sold"],   ["week_key", QTY_FIELD]]

        g_b = df_b.groupby("week_key")[QTY_FIELD].sum()
        g_s = df_s.groupby("week_key")[QTY_FIELD].sum()

        # use union of weeks so both sides align
        all_weeks = sorted(set(g_b.index).union(set(g_s.index)))
        for wk in all_weeks:
            weekly_bought_sold.append({
                "week": wk,
                "bought": int(g_b.get(wk, 0)),
                "sold":   int(g_s.get(wk, 0)),
            })
    # owner-scoped base queryset for all calculations
    txns_all = (
        Transaction.objects
        .filter(owner=user)           # or request.user
        .select_related(MEDICINE_FK)  # speeds up medicine name access
    )

    # ---- recent transactions (last 15, detailed) ----
    recent_qs = txns_all.order_by(f"-{TXN_DATE_FIELD}")[:15]

    recent_transactions = []
    for t in recent_qs:
        # date -> ISO string (date only if it's a DateTimeField)
        dtv = getattr(t, TXN_DATE_FIELD, None)
        if hasattr(dtv, "date"):
            dtv = dtv.date()

        med = getattr(t, MEDICINE_FK, None)
        qty = int(getattr(t, QTY_FIELD, 0) or 0)
        unit_price = float(getattr(t, PRICE_FIELD, 0.0) or 0.0)

        # partner can be 'partner_name' or 'partner' — use whichever exists
        partner = getattr(t, "partner_name", None)
        if not partner:
            partner = getattr(t, "partner", "-")

        recent_transactions.append({
            "date": dtv.isoformat() if dtv else "-",
            "type": getattr(t, TXN_TYPE_FIELD, "-"),
            "partner": partner,
            "medicine": getattr(med, "name", "-") if med else "-",
            "unit_price": unit_price,
            "qty": qty,
            "total": float(qty * unit_price),
        })



    # --------- Detailed profit table (per medicine) --
    detailed_rows = []
    if not df_meds.empty:
        df_meds["on_hand"] = df_meds[ON_HAND_FIELD].fillna(0).astype(int)
        df_meds["cost"] = df_meds[COST_FIELD].fillna(0.0).astype(float)

        sold_qty = df.loc[df["is_sold"]].groupby("med_name")[QTY_FIELD].sum() if not df.empty else pd.Series(dtype=float)
        revenue  = df.loc[df["is_sold"]].groupby("med_name")["amount"].sum() if not df.empty else pd.Series(dtype=float)
        bought_qty = df.loc[df["is_bought"]].groupby("med_name")[QTY_FIELD].sum() if not df.empty else pd.Series(dtype=float)

        # align by medicine name
        meds_names = df_meds["name"].tolist()
        s_bought = bought_qty.reindex(meds_names).fillna(0).astype(int)
        s_sold   = sold_qty.reindex(meds_names).fillna(0).astype(int)
        s_rev    = revenue.reindex(meds_names).fillna(0.0).astype(float)

        for i, row in df_meds.iterrows():
            name = row["name"]
            bought = int(s_bought.get(name, 0))
            sold   = int(s_sold.get(name, 0))
            rem    = int(row["on_hand"])
            cost   = float(row["cost"])
            rev    = float(s_rev.get(name, 0.0))
            cogs   = float(sold * cost)
            expired_loss = float(rem * cost) if (pd.notna(row[EXPIRY_FIELD]) and row[EXPIRY_FIELD] < today) else 0.0
            profit = float(rev - cogs - expired_loss)
            profit_pct = float((profit / rev) * 100.0) if rev else 0.0

            detailed_rows.append({
                "medicine": name, "bought": bought, "sold": sold, "remaining": rem,
                "revenue": rev, "cogs": cogs, "expired_loss": expired_loss,
                "profit": profit, "profit_pct": profit_pct
            })

    # --------- Totals & Plotly datasets --------------
    total_profit = float(sum(r["profit"] for r in detailed_rows))
    expired_loss_total = float(sum(r["expired_loss"] for r in detailed_rows))
    total_revenue_overall = float(sum(r["revenue"] for r in detailed_rows))
    profit_pct_overall = (total_profit / total_revenue_overall * 100.0) if total_revenue_overall else None

    # Inventory & profit for Plotly bars
    inv_by_medicine   = [{"name": r["medicine"], "remaining": r["remaining"]} for r in detailed_rows]
    profit_by_medicine= [{"name": r["medicine"], "profit": r["profit"]} for r in detailed_rows]

    # --------- Context to template -------------------
    # Get manufacturers for filter dropdown (Manufacturer doesn't have owner field)
    manufacturers = list(Manufacturer.objects.all().values('id', 'name'))
    
    # Calculate growth metrics
    prev_month_start = (start_of_month - timedelta(days=1)).replace(day=1)
    prev_month_end = start_of_month - timedelta(days=1)
    
    prev_month_revenue = 0.0
    if not df.empty:
        prev_month_mask = df["date_only"].between(prev_month_start, prev_month_end)
        prev_month_revenue = float((df.loc[df["is_sold"] & prev_month_mask, "amount"]).sum())
    
    revenue_growth = 0.0
    if prev_month_revenue > 0:
        revenue_growth = ((rev_month - prev_month_revenue) / prev_month_revenue) * 100
    
    # Low stock alerts (items with quantity < 10)
    low_stock_items = []
    if not df_meds.empty:
        low_stock_df = df_meds[df_meds[ON_HAND_FIELD] < 10]
        low_stock_items = [{"name": r["name"], "qty": int(r[ON_HAND_FIELD])} for _, r in low_stock_df.iterrows()]
    
    # Category/Manufacturer wise breakdown
    manufacturer_sales = []
    meds_with_mfr = Medicine.objects.filter(owner=user).select_related('manufacturer').values('name', 'manufacturer__name')
    med_to_mfr = {m['name']: m['manufacturer__name'] or 'Unknown' for m in meds_with_mfr}
    
    if not df.empty:
        df["manufacturer"] = df["med_name"].map(med_to_mfr).fillna("Unknown")
        mfr_sales = df.loc[df["is_sold"]].groupby("manufacturer")["amount"].sum().sort_values(ascending=False)
        manufacturer_sales = [{"name": n, "revenue": float(v)} for n, v in mfr_sales.items()]
    
    # Monthly trend for comparison
    monthly_trend = []
    if not df.empty:
        df["month_key"] = df[TXN_DATE_FIELD].dt.to_period("M").astype(str)
        monthly_rev = df.loc[df["is_sold"]].groupby("month_key")["amount"].sum()
        monthly_bought = df.loc[df["is_bought"]].groupby("month_key")["amount"].sum()
        all_months = sorted(set(monthly_rev.index).union(set(monthly_bought.index)))
        for m in all_months[-12:]:  # Last 12 months
            monthly_trend.append({
                "month": m,
                "revenue": float(monthly_rev.get(m, 0)),
                "expenses": float(monthly_bought.get(m, 0))
            })
    
    context = {
        # cards
        "rev_day": rev_day, "rev_week": rev_week, "rev_month": rev_month, "rev_year": rev_year,
        "total_transactions": total_transactions, "units_sold": units_sold, "avg_order_value": avg_order_value,
        "total_profit": total_profit, "expired_loss_total": expired_loss_total, "profit_pct_overall": profit_pct_overall,
        
        # growth & alerts
        "revenue_growth": revenue_growth,
        "low_stock_items": low_stock_items,
        "low_stock_count": len(low_stock_items),

        # data for tables
        "recent_transactions": recent_transactions,
        "detailed_rows": detailed_rows,
        
        # filter options
        "manufacturers": manufacturers,
        "report_type": report_type,
        "date_from": date_from,
        "date_to": date_to,

        # Plotly payloads (arrays/objects)
        "revenue_timeseries": revenue_timeseries,
        "top_medicines": top_medicines,
        "expiry_pie": expiry_pie,
        "weekly_bought_sold": weekly_bought_sold,
        "inv_by_medicine": inv_by_medicine,
        "profit_by_medicine": profit_by_medicine,
        "manufacturer_sales": manufacturer_sales,
        "monthly_trend": monthly_trend,
    }
    return render(request, "reports/reports.html", context)
