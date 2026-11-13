"""GIE AGSI historical EU storage; TTF forward market prices supplied separately."""
import os
import pandas as pd
import requests

def fetch_gie_agsi_eu(start,end,api_key=None,max_pages=100):
    """Retrieve EU aggregate storage fill (%). API needs personal GIE key.
    GIE AGSI attribution MUST accompany any use/republication.
    """
    token=api_key or os.environ.get("GIE_API_KEY")
    if not token: raise ValueError("Set GIE_API_KEY locally; never commit it")
    rows=[]
    for page in range(1,max_pages+1):
        resp=requests.get("https://agsi.gie.eu/api",headers={"x-key":token},
                          params={"type":"eu","from":start,"to":end,"size":300,"page":page},timeout=40)
        resp.raise_for_status()
        doc=resp.json()
        records=doc.get("data",[])
        if not isinstance(records,list):raise ValueError("Unexpected GIE AGSI data shape")
        rows.extend(records)
        last=int(doc.get("last_page",1))
        if page>=last:break
    else:
        raise ValueError("Maximum API pages exceeded")
    if not rows: raise ValueError("No GIE AGSI EU storage observations")
    out=pd.DataFrame(rows)
    if not {"gasDayStart","full"}.issubset(out.columns):raise ValueError("Missing GIE date/full fields")
    storage=out[["gasDayStart","full"]].rename(columns={"gasDayStart":"date","full":"storage_pct"})
    storage["date"]=pd.to_datetime(storage.date,errors="coerce")
    storage["storage_pct"]=pd.to_numeric(storage.storage_pct.astype(str).str.replace(",",".",regex=False),errors="coerce")
    storage=storage.dropna().drop_duplicates("date").sort_values("date").reset_index(drop=True)
    if not storage.storage_pct.between(0,100).all():raise ValueError("Invalid GIE storage percentage")
    return storage

def ex_ante_seasonal_reference(storage,min_prior_years=2):
    """For each MM-DD, mean storage from preceding calendar years only.
    Missing early years remain NaN. Excludes Feb 29 from matching ordinary years.
    """
    d=storage.sort_values("date").copy()
    d["mmdd"]=pd.to_datetime(d.date).dt.strftime("%m-%d")
    d["seasonal_reference_pct"]=(d.groupby("mmdd")["storage_pct"]
                                   .transform(lambda x:x.shift(1).expanding(min_periods=min_prior_years).mean()))
    return d.drop(columns="mmdd")
