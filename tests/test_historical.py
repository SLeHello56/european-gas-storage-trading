import pandas as pd
import pytest
from gas_storage.historical import fetch_gie_agsi_eu,ex_ante_seasonal_reference
class FakeResponse:
    def raise_for_status(self):pass
    def json(self):
        return {'last_page':1,'data':[{'gasDayStart':'2025-11-01','full':'79.3'},{'gasDayStart':'2025-11-02','full':'80.1'}]}
def test_gie_requires_key(monkeypatch):
    monkeypatch.delenv('GIE_API_KEY',raising=False)
    with pytest.raises(ValueError,match='GIE_API_KEY'):fetch_gie_agsi_eu('2025-11-01','2025-11-02')
def test_gie_parser(monkeypatch):
    monkeypatch.setattr('gas_storage.historical.requests.get',lambda *a,**kw:FakeResponse())
    d=fetch_gie_agsi_eu('2025-11-01','2025-11-02',api_key='test-not-real')
    assert d.storage_pct.tolist()==[79.3,80.1]
def test_ex_ante_benchmark():
    d=pd.DataFrame({'date':pd.to_datetime(['2022-11-01','2023-11-01','2024-11-01','2025-11-01']),
                    'storage_pct':[40,50,90,80]})
    out=ex_ante_seasonal_reference(d)
    assert pd.isna(out.seasonal_reference_pct.iloc[1])
    assert out.seasonal_reference_pct.iloc[2]==45
    assert out.seasonal_reference_pct.iloc[3]==60
