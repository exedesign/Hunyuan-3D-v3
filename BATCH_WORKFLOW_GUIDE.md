# Batch Image to 3D - ComfyUI Workflow Kullanım Kılavuzu

## Yöntem 2: ComfyUI Workflow ile Batch İşleme

### 🚀 Hızlı Başlangıç (3 Adım)

#### Adım 1: Workflow'u Yükleyin
1. ComfyUI'yi açın
2. **Menu** → **Load** → Workflow seçin
3. `ComfyUI-Hunyuan3D-v3/examples/batch_image_to_3d_workflow.json` dosyasını seçin

#### Adım 2: API Bilgilerini Girin
**HunyuanConfig** node'unda:
- `secret_id`: Tencent Cloud Secret ID'nizi girin
- `secret_key`: Tencent Cloud Secret Key'inizi girin
- `region`: `ap-singapore` (değiştirmeyin)

#### Adım 3: Batch İşleme Başlatın

**Manuel Yöntem (Her Image İçin):**
```
1. LoadImage node'unda image seçin (örn: cat001.png)
2. "Queue Prompt" butonuna tıklayın
3. İşlem başlasın (2-5 dakika)
4. Sonraki image'ı seçin (cat002.png)
5. Tekrar "Queue Prompt"
6. Tüm image'lar için tekrarlayın
```

**Hızlı Yöntem (Klavye ile):**
```
1. Image'ları sıralı isimlendirin: img001.png, img002.png, img003.png...
2. İlk image'ı seçin (img001.png)
3. Queue Prompt tıklayın
4. ↑ (Yukarı Ok) tuşuna basın → Bir sonraki image seçilir
5. Queue Prompt tıklayın
6. 4-5'i tekrarlayın
```

---

## 📁 Dosya Organizasyonu

### Image'ları Hazırlayın

**Önerilen İsimlendirme:**
```
input/
├── product_001.png
├── product_002.png
├── product_003.png
├── product_004.png
└── product_005.png
```

**Image'ları ComfyUI'ye Yükleyin:**
1. Image'ları `ComfyUI/input/` klasörüne kopyalayın
2. Veya LoadImage node'unda **Upload** butonunu kullanın

### Çıktı Konumu

Tüm 3D modeller burada kaydedilir:
```
ComfyUI/models/3d_models/
├── image_to_3d_20251211_143022.glb
├── image_to_3d_20251211_143255.glb
└── image_to_3d_20251211_143510.glb
```

---

## ⚙️ Parametreler

### HunyuanImageTo3D Node Ayarları

| Parametre | Değerler | Açıklama | Öneri |
|-----------|----------|----------|-------|
| **enable_pbr** | True/False | Fiziksel bazlı malzemeler | `False` (hızlı) |
| **face_count** | 40K - 1.5M | Poligon sayısı | `500K` (dengeli) |
| **generate_type** | Normal/LowPoly/Geometry/Sketch | 3D stil | `Normal` |
| **polygon_type** | triangle/quadrilateral | Poligon tipi | `triangle` |
| **max_wait_time** | 60-3600 sn | Maksimum bekleme | `600` (10 dk) |

### Önerilen Ayar Kombinasyonları

**Hızlı Test (Draft):**
- Face Count: `40000`
- Generate Type: `LowPoly`
- PBR: `False`
- ⏱️ Süre: ~2 dakika

**Dengeli Kalite:**
- Face Count: `500000`
- Generate Type: `Normal`
- PBR: `False`
- ⏱️ Süre: ~3 dakika

**Yüksek Kalite:**
- Face Count: `1500000`
- Generate Type: `Normal`
- PBR: `True`
- ⏱️ Süre: ~5 dakika

**Oyun Asset'i:**
- Face Count: `100000`
- Generate Type: `LowPoly`
- PBR: `False`
- ⏱️ Süre: ~2 dakika

---

## 🔄 Batch İşleme Stratejileri

### Strateji 1: Küçük Gruplar (Önerilen)
```
1. İlk 3-5 image'ı işleyin
2. Sonuçları kontrol edin
3. Ayarları gerekirse düzenleyin
4. Devam edin
```

**Avantajlar:**
- Hataları erken yakalar
- API kredisi israfı önler
- Kalite kontrolü kolay

### Strateji 2: Test + Production
```
1. Tek bir test image işleyin
2. Sonucu GLB viewer ile inceleyin
3. Ayarları optimize edin
4. Tüm batch'i işleyin
```

### Strateji 3: Paralel İşleme
```
1. ComfyUI'yi 2-3 kez açın (farklı portlarda)
2. Her instance'a farklı image grubu verin
3. Paralel işleme
```

⚠️ **Dikkat:** API rate limit'i kontrol edin!

---

## 📊 İlerleme Takibi

### ComfyUI Console'da Görecekleriniz:

```
🚀 Job ID: job_abc123def456
⏳ Progress: Waiting in queue (5.0%)
⏳ Progress: Processing (45.0%)
⏳ Progress: Generating geometry (75.0%)
⏳ Progress: Finalizing (95.0%)
✅ Model saved: ComfyUI/models/3d_models/image_to_3d_20251211_143022.glb
```

### ShowText Node:
Model kaydedilen tam yol görünür.

---

## 🐛 Sorun Giderme

### "ResourceInsufficient" Hatası
**Neden:** API kredisi yetersiz  
**Çözüm:**
1. https://console.intl.cloud.tencent.com/ → Billing
2. Kredi ekleyin ($10+ önerilir)
3. Tekrar deneyin

### "Tensor has no attribute astype" Hatası
**Neden:** Node versiyonu güncel değil  
**Çözüm:**
```bash
cd ComfyUI/custom_nodes/Hunyuan-3D-v3
git pull
# ComfyUI'yi yeniden başlatın
```

### Image Seçilmiyor
**Neden:** Dosya formatı desteklenmiyor  
**Çözüm:**
- PNG, JPG, JPEG, WEBP kullanın
- Image'ı `ComfyUI/input/` klasörüne kopyalayın

### Queue Donuyor
**Neden:** API timeout veya bağlantı sorunu  
**Çözüm:**
1. `max_wait_time` değerini artırın (900)
2. Internet bağlantısını kontrol edin
3. API key'leri doğrulayın

### Model Yüklenmiyor (Preview3D)
**Neden:** Preview3D GLB formatını desteklemiyor olabilir  
**Çözüm:**
- Model kaydedildi, dosya yolunu ShowText'ten alın
- Blender, Online GLB Viewer kullanın
- https://gltf-viewer.donmccurdy.com/

---

## 💡 İpuçları

### Hız Optimizasyonu:
- ✅ `face_count`: 40K-100K (düşük tutun)
- ✅ `enable_pbr`: False
- ✅ `generate_type`: LowPoly
- ⏱️ ~1.5-2 dakika/image

### Kalite Optimizasyonu:
- ✅ `face_count`: 1M-1.5M
- ✅ `enable_pbr`: True
- ✅ `generate_type`: Normal
- ⏱️ ~4-5 dakika/image

### Maliyet Optimizasyonu:
- Test ederken LowPoly + 40K kullanın
- Production için Normal + 500K kullanın
- Her request ~$0.10-0.60 arası

### Image Kalitesi:
- ✅ Yüksek çözünürlük (1024x1024+)
- ✅ İyi aydınlatma
- ✅ Temiz arka plan
- ✅ Obje merkezde
- ❌ Bulanık, düşük çözünürlük
- ❌ Çok karmaşık arka plan

---

## 📋 Checklist

Batch işleme öncesi kontrol edin:

- [ ] API credentials girildi (HunyuanConfig)
- [ ] Image'lar hazır ve yüklendi
- [ ] Image isimleri sıralı (001, 002, ...)
- [ ] Parametreler ayarlandı
- [ ] İlk test image işlendi ve kontrol edildi
- [ ] API kredisi yeterli ($10+)
- [ ] Output klasörü hazır
- [ ] ComfyUI console açık (ilerleme için)

---

## 🎯 Örnek Batch İşleme Senaryosu

**Senaryo:** 20 ürün fotoğrafını 3D modele çevir

### Adım Adım:

**1. Hazırlık (5 dakika)**
```bash
# Image'ları yeniden adlandır
product_001.png - product_020.png

# ComfyUI input klasörüne kopyala
cp *.png ~/ComfyUI/input/
```

**2. Test (3 dakika)**
```
- İlk image'ı yükle (product_001.png)
- Ayarlar: LowPoly, 100K faces, PBR: False
- Queue Prompt
- Sonucu kontrol et
```

**3. Production Ayarları (1 dakika)**
```
- Face count: 500K
- Generate type: Normal
- PBR: False
```

**4. Batch İşleme (60-100 dakika)**
```
- product_001.png seç → Queue
- ↑ tuşu → product_002.png → Queue
- ↑ tuşu → product_003.png → Queue
- ... (20 image için tekrarla)
```

**5. Sonuçları Topla**
```
cd ComfyUI/models/3d_models/
# 20 GLB dosyası oluşturuldu
```

**Toplam Süre:** ~90 dakika (20 image için)  
**Maliyet:** ~$2-8 (image kalitesine göre)

---

## 📞 Destek

**GitHub:** https://github.com/exedesign/Hunyuan-3D-v3  
**Issues:** https://github.com/exedesign/Hunyuan-3D-v3/issues  
**Tencent Cloud Docs:** https://www.tencentcloud.com/document/product/1166

---

## ✅ Başarılı Batch İşleme!

Workflow hazır! Queue Prompt'a basmaya başlayabilirsiniz! 🚀
