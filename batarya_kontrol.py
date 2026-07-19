def check_safety_limits(soc, raw_action):
    """Bataryanın fiziksel sağlığını koruyan nihai güvenlik kapısı."""
    if soc <= 20 and raw_action == "SAT (Deşarj)":
        return "BEKLE", "Güvenlik: SoC %20 sınırında, batarya sağlığı için deşarj durduruldu."
    if soc >= 80 and raw_action == "AL (Şarj)":
        return "BEKLE", "Güvenlik: SoC %80 sınırında, aşırı şarjı önlemek için işlem durduruldu."
    return raw_action, None

def evaluate_system_state(soc, ptf, solar, wind, future_solar_low=False, future_wind_low=False):
    """
    Batarya şarj ve deşarj kurallarını işletir.
    Operatöre AL / SAT / BEKLE kararı döner.
    """
    action = "BEKLE"
    reason = "Mevcut piyasa ve üretim koşulları stabil. Batarya sağlığı korunuyor."
    warnings = []

    # Sistem Uyarıları
    if soc < 25: warnings.append("⚠ SoC Kritik Seviyede")
    if solar < 20: warnings.append("⚠ Güneş Üretimi Düşük")
    if wind < 20: warnings.append("⚠ Rüzgâr Üretimi Düşük")
    if soc > 80: warnings.append("⚠ Batarya Korunuyor (Kapasite Dolu)")

    # KURAL 1: SoC < %20 ve Güneş yüksek -> Güneşten şarj et
    if soc < 20 and solar > 50:
        action = "AL (Şarj)"
        reason = "SoC düşük ve Güneş üretimi yüksek. Batarya doğrudan güneşten şarj ediliyor."
        
    # KURAL 2: SoC < %20, Güneş düşük ama Rüzgar yüksek -> Rüzgardan depola
    elif soc < 20 and solar <= 50 and wind > 50:
        action = "AL (Şarj)"
        reason = "Güneş yetersiz ancak Rüzgâr üretimi yüksek. Enerji rüzgârdan depolanıyor."
        
    # KURAL 3: PTF düşük ve Batarya dolu değil -> Piyasadan ucuz depolama
    elif ptf < 1800 and soc < 80:
        action = "AL (Şarj)"
        reason = "PTF fiyatları düşük. Arbitraj fırsatı için şebekeden ucuz enerji depolanıyor."
        warnings.append("⚠ Depolama Öneriliyor")

    # KURAL 4: PTF yüksek ve SoC > %40 -> Şebekeye enerji sat
    elif ptf > 2500 and soc > 40:
        action = "SAT (Deşarj)"
        reason = "PTF (Piyasa Takas Fiyatı) yüksek. Kâr maksimizasyonu için şebekeye satış öneriliyor."
        warnings.append("⚠ Satış Öneriliyor")

    # KURAL 5 & 6: SoC > %80 durumu
    elif soc >= 80:
        if future_solar_low and future_wind_low:
             action = "BEKLE"
             reason = "Önümüzdeki 7 gün üretim düşük tahmini var. Batarya %70-80 bandında rezerve ediliyor."
        else:
             action = "BEKLE"
             reason = "SoC %80 sınırında. Yeni depolama yapılmayacak."

    # Nihai Donanım Güvenlik Kontrolü (%20 ve %80 hard limitleri)
    final_action, safety_reason = check_safety_limits(soc, action)
    if final_action != action:
        reason = safety_reason

    return final_action, reason, warnings