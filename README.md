# Platform 13 菜單

Platform 13 全蔬食咖啡店的線上菜單。手機打開就能用：分類可以左右滑，點進分類看品項、價格和照片，也能直接搜尋。

網址：https://rolanthhuang.github.io/platform13menu/

## 改菜單

所有品項、價格、照片對應都在 `assets/js/menu-data.js`，改完存檔推上 GitHub 就會更新。

- 價格：數字（`200`）、冷熱分開（`{ hot: 130, ice: 140 }`），或文字（`'以現場報價為準'`）
- 標籤：`'decaf'` 無咖啡因、`'season'` 季節限定、`'pot'` 熱飲一壺
- 照片：`imgs` 第一張是封面；`kind: 'photo'` 是實拍，`kind: 'illust'` 會標「插畫示意」；留空就顯示「照片準備中」

## 補照片

```
python3 tools/add_photo.py 你的照片.jpg latte
```

會產生 `assets/img/photos/latte.webp` 和縮圖 `latte-sm.webp`，再把該品項的 `imgs` 改成 `[{ src: 'photos/latte', kind: 'photo' }]`。

## 字型

中文字型是霞鶩文楷 TC（SIL Open Font License），只保留網站用到的字，所以檔案很小。新增品項如果有新的字，執行一次 `tools/build_fonts.py`（說明在檔案開頭）；沒執行的話，新字會用系統字型顯示，不影響使用。

## 版本

- 正式版（首頁）：時鐘下，以 Flinders Street Station 為靈感
- `/v1/`：第一版；`/a/` 花磚、`/b/` 夜車：設計樣板
- 舊的 `/c/` 網址會自動轉到首頁

## 其他

- `tools/illustrations/`：缺照片品項的插畫產生程式
- `tools/textures.py`：砂岩、木紋、舊漆、紙張貼圖
- 價格以現場為準
