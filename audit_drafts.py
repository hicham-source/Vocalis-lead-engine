import sqlite3
import yaml
import json
import os
from database import get_connection

def calculate_revenue_loss(niche, config):
    niches_cfg = config.get("niches", {})
    cfg = niches_cfg.get(niche.lower(), {
        "calls_per_day": 30,
        "miss_rate": 0.3,
        "booking_rate": 0.4,
        "avg_ticket_sar": 800
    })
    calls = cfg.get("calls_per_day", 30)
    miss = cfg.get("miss_rate", 0.3)
    book = cfg.get("booking_rate", 0.4)
    ticket = cfg.get("avg_ticket_sar", 800)
    
    monthly_loss = calls * miss * book * ticket * 30
    return monthly_loss

def generate_audit_and_drafts():
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
        
    conn = get_connection()
    c = conn.cursor()
    
    # التأكد من وجود أعمدة نقاط القوة والضعف
    try:
        c.execute("ALTER TABLE leads ADD COLUMN strengths TEXT")
        c.execute("ALTER TABLE leads ADD COLUMN weaknesses TEXT")
    except sqlite3.OperationalError:
        pass
        
    leads = c.execute("SELECT place_id, name, niche, rating, review_count, has_booking, website, phone, address FROM leads").fetchall()
    
    for row in leads:
        pid, name, niche, rating, reviews, has_booking, website, phone, address = row
        loss = calculate_revenue_loss(niche or "dental clinic", config)
        
        # تحليل نقاط القوة
        strengths = []
        if rating and rating >= 4.3:
            strengths.append(f"سمعة قوية وتقييم ممتاز ({rating} نجوم)")
        if reviews and reviews > 300:
            strengths.append(f"قاعدة عملاء واسعة ونشطة ({reviews} مراجعة)")
        if website:
            strengths.append("تواجد رقمي وموقع إلكتروني معتمد")
        if not strengths:
            strengths.append("موقع تجاري نشط في نطاق الرياض")
            
        # تحليل نقاط الضعف
        weaknesses = []
        if not has_booking:
            weaknesses.append("عدم توفر نظام حجز فوري مؤتمت (اعتماد كلي على الاتصال)")
        weaknesses.append("فقدان محتمل للعملاء خارج ساعات العمل ونهاية الأسبوع")
        if not phone or str(phone).startswith("011"):
            weaknesses.append("صعوبة التواصل السريع المباشر عبر واتساب")
            
        strengths_str = " • " + "\n • ".join(strengths)
        weaknesses_str = " • " + "\n • ".join(weaknesses)
        
        # تخصيص مسودة الواتساب بناءً على النتيجة الواقعية
        wa_text = (
            f"مساء الخير يا دكتور / فريق {name}، يعطيكم العافية.\n"
            f"ما شاء الله لفت انتباهنا تقييمكم العالي ({rating or 4.5}⭐) وثقة المراجعين فيكم.\n"
            f"لاحظنا فقط أن الحجز معتمد كلياً على الاتصال بدون رد آلي سريع، وهالشيء غالباً يضيّع جزء من الحجوزات وقت الذروة وبعد الدوام.\n"
            f"طوّرنا نظام استقبال ومساعد صوتي ذكي يخدمكم بنفس لهجة الرياض ويأكد الحجوزات 24/7.\n"
            f"يناسبكم نجرب اتصال تجريبي مدته دقيقتين؟"
        )
        
        c.execute("""
            UPDATE leads 
            SET revenue_loss_sar = ?, strengths = ?, weaknesses = ?, whatsapp_draft = ?
            WHERE place_id = ?
        """, (loss, strengths_str, weaknesses_str, wa_text, pid))
        
    conn.commit()
    conn.close()
    print("تم تحديث نقاط القوة والضعف والمسودات لجميع المنشآت بنجاح!")

if __name__ == "__main__":
    generate_audit_and_drafts()
