# SECURITY.md — Hướng dẫn dọn secret đã lộ trên Git history

> Chạy **trước khi bật lại production**, sau khi đã push code fix bảo mật.

## 1. Rotate secret (GCP Console / local .env)

- [ ] Đổi password Cloud SQL user `cms_user`
- [ ] Generate `API_SECRET_KEY` mới → cập nhật `.env` backend + GitHub Secrets CMS + `--dart-define` App
- [ ] Tạo GCP SA key Gemini **mới** (key cũ Google đã disable)

## 2. GitHub Secrets (repo `UI_web_he_thong_and`)

Settings → Secrets → Actions → thêm:

| Secret | Nguồn |
|---|---|
| `GCP_SA_KEY` | JSON SA deploy GCS (đã có) |
| `VITE_APP_API_SECRET` | Cùng `API_SECRET_KEY` backend |
| `VITE_RECAPTCHA` | reCAPTCHA site key |
| `VITE_FIREBASE_API_KEY` | Firebase Console → Web App |
| `VITE_FIREBASE_AUTH_DOMAIN` | Firebase Console |
| `VITE_FIREBASE_PROJECT_ID` | Firebase Console |
| `VITE_FIREBASE_STORAGE_BUCKET` | Firebase Console |
| `VITE_FIREBASE_MESSAGING_SENDER_ID` | Firebase Console |
| `VITE_FIREBASE_APP_ID` | Firebase Console |
| `VITE_FIREBASE_MEASUREMENT_ID` | Firebase Console (tuỳ chọn) |

## 3. Xóa secret khỏi git history

### Repo API (`API_web_he_thong_and_app`)

```bash
pip install git-filter-repo
git filter-repo --path project-f3e21dd2-0270-45f3-91c-392a0d4991a3.json --invert-paths --force
git push origin main --force
```

### Repo UI (`UI_web_he_thong_and`)

```bash
git filter-repo --path .env --path .env.development --path .env.production --invert-paths --force
git push origin main --force
```

> Team cần `git clone` lại hoặc `git fetch && git reset --hard origin/main`.

## 4. Kiểm tra

```bash
git log --all --full-history -- "**/.env" "**/*392a0d4991*"
# Không còn kết quả

grep -r "VLU15122004" src/ app/ lib/ 2>/dev/null
# Không còn trong source (trừ .env local gitignored)
```
