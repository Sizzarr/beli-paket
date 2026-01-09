from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.client.engsel import get_balance, get_tiering_info
from app.service.auth import AuthInstance

app = FastAPI()
templates = Jinja2Templates(directory="templates")

MENU_ITEMS = [
    {
        "id": "account",
        "label": "Login/Ganti akun",
        "description": "Kelola akun XL dan refresh token tersimpan.",
        "icon": "\ud83d\udc64",
    },
    {
        "id": "packages",
        "label": "Lihat Paket Saya",
        "description": "Lihat paket aktif beserta detail kuota.",
        "icon": "\ud83d\udce6",
    },
    {
        "id": "hot",
        "label": "Beli Paket \ud83d\udd25 HOT",
        "description": "Promo paket terpanas pilihan MyXL.",
        "icon": "\ud83d\udd25",
    },
    {
        "id": "hot2",
        "label": "Beli Paket \ud83d\udd25 HOT-2",
        "description": "Alternatif rekomendasi paket populer.",
        "icon": "\ud83c\udf1f",
    },
    {
        "id": "option-code",
        "label": "Beli Paket Berdasarkan Option Code",
        "description": "Beli paket menggunakan kode opsi khusus.",
        "icon": "\ud83d\udd22",
    },
    {
        "id": "family-code",
        "label": "Beli Paket Berdasarkan Family Code",
        "description": "Temukan paket dari family code tertentu.",
        "icon": "\ud83d\udd11",
    },
    {
        "id": "loop",
        "label": "Beli Semua Paket di Family Code",
        "description": "Otomatis beli semua opsi dalam family code.",
        "icon": "\ud83d\udd01",
    },
    {
        "id": "transactions",
        "label": "Riwayat Transaksi",
        "description": "Pantau pembelian paket dan histori transaksi.",
        "icon": "\ud83d\udcc4",
    },
    {
        "id": "family-plan",
        "label": "Family Plan/Akrab Organizer",
        "description": "Kelola grup Akrab & family plan XL.",
        "icon": "\ud83d\udc6a",
    },
    {
        "id": "circle",
        "label": "Circle",
        "description": "Akses fitur circle untuk komunitas.",
        "icon": "\ud83e\udded",
    },
    {
        "id": "store-segments",
        "label": "Store Segments",
        "description": "Lihat segmen store dan penawaran khusus.",
        "icon": "\ud83d\udecd\ufe0f",
    },
    {
        "id": "store-family",
        "label": "Store Family List",
        "description": "Eksplorasi daftar family di store.",
        "icon": "\ud83d\uddc2\ufe0f",
    },
    {
        "id": "store-packages",
        "label": "Store Packages",
        "description": "Cari paket di katalog store.",
        "icon": "\ud83d\udce6",
    },
    {
        "id": "redeemables",
        "label": "Redemables",
        "description": "Daftar hadiah yang bisa ditukar.",
        "icon": "\ud83c\udf81",
    },
    {
        "id": "register",
        "label": "Register",
        "description": "Registrasi nomor baru dengan dukcapil.",
        "icon": "\ud83d\udcdd",
    },
    {
        "id": "notifications",
        "label": "Notifikasi",
        "description": "Kelola notifikasi dan pesan terbaru.",
        "icon": "\ud83d\udd14",
    },
    {
        "id": "validate",
        "label": "Validate msisdn",
        "description": "Validasi msisdn untuk memastikan akun.",
        "icon": "\u2705",
    },
    {
        "id": "bookmark",
        "label": "Bookmark Paket",
        "description": "Simpan paket favorit untuk akses cepat.",
        "icon": "\ud83d\udd16",
    },
    {
        "id": "exit",
        "label": "Tutup aplikasi",
        "description": "Keluar dari aplikasi dengan aman.",
        "icon": "\ud83d\udeaa",
    },
]


def build_profile():
    active_user = AuthInstance.get_active_user()
    if not active_user:
        return None

    balance_data = get_balance(AuthInstance.api_key, active_user["tokens"]["id_token"])
    balance_remaining = balance_data.get("remaining")
    balance_expired_at = balance_data.get("expired_at")
    point_info = "Points: N/A | Tier: N/A"

    if active_user["subscription_type"] == "PREPAID":
        tiering_data = get_tiering_info(AuthInstance.api_key, active_user["tokens"])
        tier = tiering_data.get("tier", 0)
        current_point = tiering_data.get("current_point", 0)
        point_info = f"Points: {current_point} | Tier: {tier}"

    expired_at_dt = datetime.fromtimestamp(balance_expired_at).strftime("%Y-%m-%d")

    return {
        "number": active_user["number"],
        "subscription_type": active_user["subscription_type"],
        "balance": balance_remaining,
        "balance_expired_at": expired_at_dt,
        "point_info": point_info,
    }


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    profile = build_profile()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "profile": profile, "menu_items": MENU_ITEMS},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("web_app:app", host="0.0.0.0", port=5000, reload=True)
