# TIC Japan Market Brief

1. Buat repo GitHub private. Ekstrak ZIP dan commit semua file ke branch utama, termasuk folder tersembunyi .github.
2. Buat webhook baru di channel tujuan. Simpan URL-nya di Settings > Secrets and variables > Actions > New repository secret dengan nama DISCORD_WEBHOOK_URL.
3. Buka Actions > TIC Japan Market Brief > Run workflow. Jalankan tanpa mencentang send untuk preview di log, lalu jalankan dengan send dicentang untuk tes kirim.
4. Workflow terjadwal setiap hari pukul 07.00 dan 19.00 JST (22.00 dan 10.00 UTC). GitHub Actions dapat terlambat memulai job.

Emas memakai futures GC=F sebagai acuan XAUUSD spot. Nasdaq memakai futures Nasdaq-100 NQ=F. Harga dan jam bar berasal dari Yahoo Finance. Berita berupa headline sumber dari Google News RSS, maksimal tiga judul dari 12 jam terakhir. Cek artikel asli sebelum menarik kesimpulan.

Preview lokal: python -m pip install -r requirements.txt lalu python brief.py.
