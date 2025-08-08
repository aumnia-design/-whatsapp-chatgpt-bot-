from fastapi import FastAPI, Request
import os, httpx

app = FastAPI()

SYSTEM_PROMPT = """
أنت مساعد مبيعات وخدمة لعلامة BELLAM DESIGNE. ترد بالدارجة المغربية باحترام وباختصار.
المنتجات:
- طاولة الخياطة 1600 درهم: 170×80×90 سم، بلاصة الحدادة، جوج أدراج + خزانة، التوصيل مجاني ≤10 أيام أو 50 درهم ≤72 ساعة، كتدخل فالمسابقة بعد كل 10 مبيعات.
- طاولة الخياطة 1300 درهم: نفس المقاسات تقريبًا، بدون المسابقة، التوصيل مجاني.
القواعد:
1) جاوب بالمعلومة الأكيدة فقط. إذا ما كانتش واضحة، سَوّل سؤال قصير.
2) فحال نية الشراء، جمع: الاسم، المدينة، العنوان التقريبي، الهاتف، النسخة (1300/1600)، الكمية، نوع التوصيل (مجاني/سريع 50 درهم).
3) كلمات “عاجل/تتبع” = اقترح التحويل للدعم المباشر.
"""

OPENAI_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_MODEL = "gpt-4o"
TIMEOUT = 30

@app.post("/manychat-gpt")
async def manychat_gpt(req: Request):
    body = await req.json()
    user_text = body.get("text", "") or body.get("message", "") or ""
    payload = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        "temperature": 0.3
    }
    headers = {
        "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY','')}",
        "Content-Type": "application/json"
    }
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.post(OPENAI_URL, json=payload, headers=headers)
        data = r.json()
        reply = (data.get("choices",[{}])[0].get("message",{}).get("content","")).strip()
        if not reply:
            reply = "سمح ليا، ما فهمتش مزيان. واش ممكن توضّح ليا شنو بغيتي بالضبط؟"
    except Exception:
        reply = "وقع مشكل تقني صغير دابا. نقدر نربطك مع الفريق باش يعاونك بسرعة؟"
    return {"reply": reply}
