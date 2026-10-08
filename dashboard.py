import streamlit as st
import pandas as pd
from urllib.parse import quote
from database import get_connection

st.set_page_config(
    page_title="Vocalis KSA | Lead Command Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;600;700;900&display=swap');
    * { font-family: 'Tajawal', sans-serif !important; }
    
    .stApp { background-color: #0b0f19; color: #f1f5f9; }
    
    .kpi-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 22px;
        backdrop-filter: blur(12px);
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.5);
    }
    .kpi-title { font-size: 0.85rem; color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    .kpi-val { font-size: 1.85rem; font-weight: 900; margin-top: 6px; }
    
    .lead-box {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 15px 30px rgba(0,0,0,0.4);
    }
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 700;
        margin-right: 6px;
    }
    .badge-amber { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
    .badge-emerald { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-blue { background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }
    
    .btn-wa {
        display: block;
        text-align: center;
        background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
        color: white !important;
        padding: 12px 18px;
        border-radius: 12px;
        font-weight: 700;
        text-decoration: none !important;
        box-shadow: 0 4px 15px rgba(37, 211, 102, 0.3);
        margin-top: 10px;
    }
    .btn-wa:hover { opacity: 0.95; }
</style>
""", unsafe_allow_html=True)

def load_data():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM leads", conn)
    conn.close()
    return df

def update_status(pid, st_val, wa_txt=None, em_txt=None):
    conn = get_connection()
    c = conn.cursor()
    if wa_txt and em_txt:
        c.execute("UPDATE leads SET status=?, whatsapp_draft=?, email_draft=? WHERE place_id=?", (st_val, wa_txt, em_txt, pid))
    else:
        c.execute("UPDATE leads SET status=? WHERE place_id=?", (st_val, pid))
    conn.commit()
    conn.close()

df = load_data()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🎙️ **Vocalis AI Hub**")
    st.caption("نظام الاستهداف والتنقيب الآلي | الرياض")
    st.divider()
    
    if not df.empty:
        niches = ["الكل"] + sorted(list(df['niche'].dropna().unique()))
        sel_niche = st.selectbox("المجال المستهدف", niches)
        
        search_query = st.text_input("🔍 بحث عن عيادة أو حي", "")
        
        work_df = df if sel_niche == "الكل" else df[df['niche'] == sel_niche]
        if search_query:
            work_df = work_df[work_df['name'].str.contains(search_query, case=False, na=False) | 
                              work_df['address'].str.contains(search_query, case=False, na=False)]
    else:
        work_df = df

p_df = work_df[work_df['status'] == 'pending']
a_df = work_df[work_df['status'] == 'approved']
s_df = work_df[work_df['status'] == 'skipped']

# --- TOP METRICS ROW ---
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">طابور التدقيق الفوري</div>
        <div class="kpi-val" style="color: #60a5fa;">{len(p_df)}</div>
    </div>
    """, unsafe_allow_html=True)
with m2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">معتمدة للإرسال</div>
        <div class="kpi-val" style="color: #34d399;">{len(a_df)}</div>
    </div>
    """, unsafe_allow_html=True)
with m3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">المستبعدة</div>
        <div class="kpi-val" style="color: #94a3b8;">{len(s_df)}</div>
    </div>
    """, unsafe_allow_html=True)
with m4:
    total_loss = work_df['revenue_loss_sar'].sum() if 'revenue_loss_sar' in work_df else 0
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">فرص ضائعة مكتشفة</div>
        <div class="kpi-val" style="color: #f59e0b;">{total_loss:,.0f} <span style="font-size: 1rem;">SAR</span></div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# --- TABS ---
tab_lead, tab_approved, tab_raw = st.tabs(["⚡ مسار المراجعة الذكية", "✅ القائمة المعتمدة (Ready)", "🗄️ المستودع الإجمالي"])

with tab_lead:
    if p_df.empty:
        st.success("🎉 أحسنت! انتهيت من جميع العملاء في هذا القسم.")
    else:
        lead = p_df.iloc[0]
        
        c_left, c_right = st.columns([1, 1], gap="large")
        
        with c_left:
            st.markdown(f"### **{lead['name']}**")
            
            # Badges
            b_html = ""
            if pd.notna(lead['rating']):
                b_html += f'<span class="badge badge-amber">⭐ {lead["rating"]} ({int(lead["review_count"] or 0)} تقييم)</span>'
            if pd.notna(lead['niche']):
                b_html += f'<span class="badge badge-blue">{lead["niche"]}</span>'
            if lead.get('has_booking') == 0:
                b_html += '<span class="badge badge-amber">⚠️ بدون حجز إلكتروني</span>'
            st.markdown(b_html, unsafe_allow_html=True)
            
            st.markdown(f"📍 **الموقع:** {lead['address']}")
            
            c_c1, c_c2 = st.columns(2)
            with c_c1:
                if lead['phone']:
                    st.markdown(f"📞 [{lead['phone']}](tel:{lead['phone']})")
                if lead['website']:
                    st.markdown(f"🌐 [الموقع الإلكتروني]({lead['website']})")
            with c_c2:
                if lead['whatsapp']:
                    st.markdown(f"💬 واتساب: `{lead['whatsapp']}`")
                if lead['email']:
                    st.markdown(f"✉️ إيميل: `{lead['email']}`")
            
            st.markdown("---")
            st.markdown("#### 🚨 تحليل الفرصة والفاقد المالي")
            st.info(f"**نقطة الضعف الحالية:** {lead['primary_pain'] or 'عدم وجود نظام استقبال متقدم بعد ساعات العمل'}")
            
            loss_val = lead['revenue_loss_sar'] or 0
            st.metric("الفاقد التقديري شهرياً", f"{loss_val:,.0f} SAR", delta=f"{lead['niche']}", delta_color="inverse")

        with c_right:
            st.markdown("### 📝 مسودات التواصل المقترحة")
            
            wa_draft = st.text_area("رسالة الواتساب (اللهجة النجدية/البيضاء)", value=lead['whatsapp_draft'] or "", height=140)
            
            # 1-Click WhatsApp Trigger
            wa_num = lead['whatsapp'] or lead['phone']
            if wa_num and wa_draft:
                clean_digits = "".join(filter(str.isdigit, str(wa_num)))
                wa_url = f"https://wa.me/{clean_digits}&text={quote(wa_draft)}"
                st.markdown(f'<a href="{wa_url}" target="_blank" class="btn-wa">🚀 إرسال عبر تطبيق WhatsApp فوراً</a>', unsafe_allow_html=True)
                
            email_draft = st.text_area("مسودة الإيميل الرسمي", value=lead['email_draft'] or "", height=150)
            
            with st.expander("English Translation"):
                st.write(lead['english_draft'] or "No translation available")
                
            st.write("")
            b1, b2 = st.columns(2)
            if b1.button("✅ اعتماد وترقية (Approve)", use_container_width=True, type="primary"):
                update_status(lead['place_id'], 'approved', wa_draft, email_draft)
                st.rerun()
            if b2.button("⏭️ استبعاد (Skip)", use_container_width=True, type="secondary"):
                update_status(lead['place_id'], 'skipped')
                st.rerun()

with tab_approved:
    st.markdown("### 📋 العملاء الجاهزون للإغلاق والمتابعة")
    if a_df.empty:
        st.info("لم تقم باعتماد أي عميل حتى الآن.")
    else:
        csv_file = a_df[['name', 'phone', 'whatsapp', 'email', 'niche', 'rating', 'revenue_loss_sar', 'whatsapp_draft']].to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل القائمة المعتمدة بصيغة CSV جاهزة للـ CRM", data=csv_file, file_name="vocalis_approved_leads.csv", mime="text/csv")
        st.dataframe(a_df[['name', 'phone', 'whatsapp', 'niche', 'rating', 'revenue_loss_sar']], use_container_width=True)

with tab_raw:
    st.dataframe(work_df, use_container_width=True)
