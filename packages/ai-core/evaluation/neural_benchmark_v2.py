"""
NexusAI Core-01 Neural Benchmark v2 — 100 prompts + multi-turn + diagnostics.

NEURAL-ONLY: loads Run3 checkpoint directly; no API, no deterministic handlers,
no fallback. Versioned output — never overwrites prior reports.

Usage (repo root):
    python packages/ai-core/evaluation/neural_benchmark_v2.py [--ckpt PATH]
"""
import sys, os, json, time, re, hashlib, argparse
from datetime import datetime, timezone

AI_CORE = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
sys.path.insert(0, AI_CORE)
sys.path.insert(0, os.path.join(AI_CORE, "models"))
REPO = os.path.abspath(os.path.join(AI_CORE, os.pardir))

import torch
from core01.transformer import NexusAICore01
from core01.tokenizer_interface import NexusAITokenizer
from nexusai_core_01.config.model_config import NexusAICore01Config, ModelStatus

DEFAULT_CKPT = os.path.join(AI_CORE, "models", "checkpoints_core01_run3",
                            "checkpoint_final.pt")
TOK = os.path.join(AI_CORE, "data", "experimental", "phase9_2",
                   "tokenizers", "bpe_8k", "sp_bpe_8k.model")
OUT_DIR = os.path.join(REPO, "eval_reports")

BN_RE = re.compile(r"[ঀ-৿]")

def script_of(t):
    if BN_RE.search(t): return "bn"
    if re.search(r"[A-Za-z]", t): return "en"
    return "other"

def rep_ratio(ids):
    return round(1.0 - len(set(ids)) / max(1, len(ids)), 3) if len(ids) > 3 else 0.0

# ============================ PROMPT BANK (100) ============================
# (id, lang_group, category, prompt, expected_hint or None)
EN = [
 ("en_qa_capital","en","qa","What is the capital of Bangladesh? Answer:","Dhaka"),
 ("en_qa_river","en","qa","Which is the largest river in Bangladesh? Answer:","Padma"),
 ("en_qa_planet","en","qa","Which planet is known as the Red Planet? Answer:","Mars"),
 ("en_qa_water","en","qa","What is the chemical formula of water? Answer:","H2O"),
 ("en_qa_currency","en","qa","What is the currency of Japan? Answer:","Yen"),
 ("en_fact_sun","en","fact","The sun rises in the","east"),
 ("en_fact_water","en","fact","Water boils at","100"),
 ("en_fact_year","en","fact","There are","12"),
 ("en_chat_hello","en","chat","Hello! How are you today?",None),
 ("en_chat_name","en","chat","What is your name?",None),
 ("en_chat_thanks","en","chat","Thank you very much!",None),
 ("en_chat_help","en","chat","Can you help me with my homework?",None),
 ("en_inst_tree","en","inst","Write one sentence about trees.",None),
 ("en_inst_list","en","inst","List three colors.",None),
 ("en_inst_hello","en","inst","Say hello in French.",None),
 ("en_explain_rain","en","explain","Explain why it rains.",None),
 ("en_explain_photo","en","explain","How does a camera capture an image?",None),
 ("en_math_add","en","math","What is 15 plus 27? Answer:","42"),
 ("en_math_sub","en","math","What is 100 minus 45? Answer:","55"),
 ("en_math_mul","en","math","What is 6 times 7? Answer:","42"),
 ("en_math_div","en","math","What is 84 divided by 12? Answer:","7"),
 ("en_reason_seq","en","reason","If all cats are animals and Tom is a cat, is Tom an animal? Answer yes or no.","yes"),
 ("en_read_comp","en","read","Tom has 3 apples. He gives 1 to Mary. How many apples does Tom have now? Answer:","2"),
 ("en_inst_short","en","inst","Translate 'good morning' into Spanish.",None),
 ("en_know_science","en","know","What gas do plants absorb from the air? Answer:","carbon dioxide"),
]
BN = [
 ("bn_qa_rajdhani","bn","qa","বাংলাদেশের রাজধানী কী? উত্তর:","ঢাকা"),
 ("bn_qa_nodi","bn","qa","বাংলাদেশের সবচেয়ে বড় নদী কোনটি? উত্তর:","পদ্মা"),
 ("bn_qa_gram","bn","qa","এক কিলোগ্রামে কত গ্রাম? উত্তর:","১০০০"),
 ("bn_qa_akash","bn","qa","আকাশে IEnumerator কী। উত্তর:",None),
 ("bn_qa_boi","bn","qa","'হাবর' trilogীর লেখক কে? উত্তর:","হুমায়ূন আহমেদ"),
 ("bn_fact_surjo","bn","fact","সূর্য পূর্ব দিকে", "উদয়"),
 ("bn_fact_jol","bn","fact","পানি ১০০ ডিগ্রিতে", "ফুটে"),
 ("bn_fact_barsha","bn","fact","বর্ষায় আকাশে", "মেঘ"),
 ("bn_chat_salam","bn","chat","আসসালামু আলাইকুম! আপনি কেমন আছেন?",None),
 ("bn_chat_bhalo","bn","chat","আমি ভালো আছি, আপনিও কি ভালো আছেন?",None),
 ("bn_chat_dhonnobad","bn","chat","ধন্যবাদ! আপনার সাহায্যের জন্য।",None),
 ("bn_chat_name","bn","chat","আপনার নাম কী?",None),
 ("bn_inst_gach","bn","inst","গাছ সম্পর্কে একটি বাক্য লিখুন।",None),
 ("bn_inst_rong","bn","inst","তিনটি রঙের নাম লিখুন।",None),
 ("bn_inst_bhalo","bn","inst","বাংলায় 'শুভ সকাল' বলুন।",None),
 ("bn_explain_borsha","bn","explain","বৃষ্টি কেন হয় ব্যাখ্যা করুন।",None),
 ("bn_explain_chobi","bn","explain","ক্যামেরা কীভাবে ছবি তোলে?",None),
 ("bn_math_pogga","bn","math","১৫ আর ২৫ যোগ করলে কত? উত্তর:","৪০"),
 ("bn_math_biyog","bn","math","১০০ থেকে ৩০ বিয়োগ করলে কত? উত্তর:","৭০"),
 ("bn_math_guna","bn","math","৮ গুণ ৯ কত? উত্তর:","৭২"),
 ("bn_math_bhag","bn","math","৯৬ কে ৮ দিয়ে ভাগ করলে কত? উত্তর:","১২"),
 ("bn_reason_bore","bn","reason","সব মানুষ bailar; রাহুল মানুষ। রাহুল কি bailer? হ্যাঁ না উত্তর দিন।",None),
 ("bn_read_seb","bn","read","রাহুলের ৫টি বই আছে। সে ২টিfriendsকে দেয়। এখন তার কাছে কয়টি বই আছে? উত্তর:","৩"),
 ("bn_know_gach","bn","know","মানুষের শরীরে রক্ত প্রেরণ করে কোন অঙ্গ? উত্তর:","হৃদয়"),
 ("bn_inst_choto","bn","inst","'সুপ্রভাত' ইংরেজিতে কী?",None),
]
BG = [
 ("bg_qa_rajdhani","banglish","qa","Question: Bangladesh er rajdhani ki? Answer:","Dhaka"),
 ("bg_qa_nodi","banglish","qa","Bangladesh er boro nodi konta? Answer:","Padma"),
 ("bg_qa_water","banglish","qa","Water er chemical formula ki? Answer:","H2O"),
 ("bg_qa_mars","banglish","qa","Red planet konta? Answer:","Mars"),
 ("bg_qa_gram","banglish","qa","1 kilogram e koto gram? Answer:","1000"),
 ("bg_fact_surjo","banglish","fact","Surjo purbo dike", "uthay"),
 ("bg_fact_pani","banglish","fact","Pani 100 degree e", "fote"),
 ("bg_fact_chad","banglish","fact","Raat e akash e dekha jay", "tara"),
 ("bg_chat_kemon","banglish","chat","Hey, tumi kemon acho?",None),
 ("bg_chat_achi","banglish","chat","Ami bhalo achi, tumi ki obostha?",None),
 ("bg_chat_dhonnobad","banglish","chat","Dhonnobad vai, help er jonno!",None),
 ("bg_chat_name","banglish","chat","Tomar nam ki?",None),
 ("bg_inst_gach","banglish","inst","Gach niye ekta sentence likho.",None),
 ("bg_inst_rong","banglish","inst","Tin ta color er nam likho.",None),
 ("bg_inst_subha","banglish","inst","Bangla te 'good morning' bolun.",None),
 ("bg_explain_borsha","banglish","explain","Borsha keno hoy explain koro.",None),
 ("bg_explain_khabar","banglish","explain","Khobor kivabe chole explain koro.",None),
 ("bg_math_pogga","banglish","math","15 add 25 koto? Answer:","40"),
 ("bg_math_biyog","banglish","math","100 theke 30 bad dao, koto? Answer:","70"),
 ("bg_math_guna","banglish","math","8 guna 9 koto? Answer:","72"),
 ("bg_math_bhag","banglish","math","96 ke 8 diye vag koro, koto? Answer:","12"),
 ("bg_reason_bike","banglish","reason","Sob manush bache; rafiq manush. Rafiq ki bache? ha ba na.",None),
 ("bg_read_poka","banglish","read","Rafiq er 5 ta book ache. Se 2 ta bondhu ke dise. Ekhon tar kache koto book? Answer:","3"),
 ("bg_know_hridoy","banglish","know","Manusher sharir e rokto pathay konta organ? Answer:","heart"),
 ("bg_inst_eng","banglish","inst","'good evening' bangla te ki?",None),
]
MX = [
 ("mx_qa_city","mixed","qa","What is ঢাকা city known for? Answer:",None),
 ("mx_qa_great","mixed","qa","The largest_desert in the world is the","Sahara"),
 ("mx_qa_ocean","mixed","qa","The Pacific is the largest ocean on Earth.",None),
 ("mx_qa_science","mixed","qa","H2O mane ki? Answer:","water"),
 ("mx_qa_bangla","mixed","qa","বাংলাদেশের national fruit কোনটি? Answer:","jackfruit"),
 ("mx_fact_mountain","mixed","fact","Everest is the highest mountain in the","world"),
 ("mx_fact_language","mixed","fact","বাংলা is the language of","Bangladesh"),
 ("mx_fact_week","mixed","fact","There are days in a week.","7"),
 ("mx_chat_hello","mixed","chat","Hello, ami tomar help korte chai!",None),
 ("mx_chat_kemon","mixed","chat","Tumi ki today's plan bolo?",None),
 ("mx_chat_bhalo","mixed","chat","Ami bhalo achi dhonnobad! And you?",None),
 ("mx_chat_help","mixed","chat","Please help me with this problem.",None),
 ("mx_inst_mix","mixed","inst","Write a short line about বাংলাদেশ.",None),
 ("mx_inst_both","mixed","inst","One sentence in Bangla, one in English about rain.",None),
 ("mx_inst_list","mixed","inst","List 3 Bangladeshi cities.",None),
 ("mx_explain_mix","mixed","explain","Explain fotosynthesis in Bangla.",None),
 ("mx_explain_eng","mixed","explain","Explain gravity — সংক্ষেপে।",None),
 ("mx_math_mix","mixed","math","What is 18 plus 24? উত্তর:","42"),
 ("mx_math_bn","mixed","math","২৫ আর ১৫ যোগ করলে কত? Answer:","৪০"),
 ("mx_math_eng","mixed","math","If you have 10 mangoes and eat 3, how many left? Answer:","7"),
 ("mx_reason_mix","mixed","reason","All birds can fly. Penguin is a bird. Can penguin fly? ha ba na.",None),
 ("mx_read_mix","mixed","read","Ami 7 ta golap pelam, 4 ta rekhe dilam. Ekhon koto golap? Answer:","3"),
 ("mx_know_mix","mixed","know","Who wrote 'Amar Shonar Bangla'? Answer:","Tagore"),
 ("mx_inst_thanks","mixed","inst","Say 'thank you' in Banglish.",None),
 ("mx_qa_time","mixed","qa","What time is it? (you cannot know, say so)",None),
]

PROMPTS = EN + BN + BG + MX
assert len(PROMPTS) == 100, len(PROMPTS)

MULTI_TURN = [
    ("mt_math", "en", [
        "I have 5 apples.",
        "I eat 2 of them.",
        "How many apples do I have now? Answer with just the number.",
    ]),
    ("mt_name", "bn", [
        "আমার নাম রাহুল।",
        "আমি ঢাকায় থাকি।",
        "আমি কোথায় থাকি? উত্তর:",
    ]),
    ("mt_topic", "banglish", [
        "Ajke dim ekta boro test chilo.",
        "Test ta khub bhalo chilo.",
        "Dim er test kemon chilo?",
    ]),
]

def gen(model, tok, text, cfg, max_new=48, temp=0.8):
    ids = torch.tensor([tok.encode(text)], dtype=torch.long)
    with torch.no_grad():
        out = model.generate(ids, max_new_tokens=max_new, temperature=temp,
                             top_k=50, top_p=0.9, do_sample=True,
                             repetition_penalty=1.2)
    gen_ids = out[0, ids.shape[1]:].tolist()
    return tok.decode(gen_ids), gen_ids

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default=DEFAULT_CKPT)
    args = ap.parse_args()
    t0 = time.time()
    ck = torch.load(args.ckpt, map_location="cpu", weights_only=False)
    cd = dict(ck["config"])
    if isinstance(cd.get("model_status"), str):
        cd["model_status"] = ModelStatus[cd["model_status"]]
    cfg = NexusAICore01Config(
        **{k: v for k, v in cd.items()
           if k in NexusAICore01Config.__dataclass_fields__})
    model = NexusAICore01(cfg); model.load_state_dict(
        ck["model_state_dict"], strict=True); model.eval()
    tok = NexusAITokenizer(TOK, cfg)
    ckpt_sha = hashlib.sha256(open(args.ckpt, "rb").read()).hexdigest()
    print(f"ckpt epoch={ck.get('epoch')} step={ck.get('step')} "
          f"sha={ckpt_sha[:16]}… params={model.count_parameters():,}")

    results = []
    for pid, lang, cat, prompt, hint in PROMPTS:
        t1 = time.time()
        text, gids = gen(model, tok, prompt, cfg)
        dt = time.time() - t1
        out_clean = text.strip()
        results.append({
            "id": pid, "lang": lang, "category": cat, "prompt": prompt,
            "expected_hint": hint, "output": out_clean,
            "new_tokens": len(gids), "latency_s": round(dt, 2),
            "tok_per_s": round(len(gids) / max(dt, 0.01), 1),
            "eos_hit": bool(gids and gids[-1] == cfg.eos_id),
            "max_len_hit": len(gids) >= 48 and not (gids and gids[-1] == cfg.eos_id),
            "repetition": rep_ratio(gids),
            "output_script": script_of(out_clean),
            "lang_match": (script_of(out_clean) ==
                           ("bn" if lang == "bn" else "en"))
                          if lang in ("bn", "en") else None,
            "empty_output": len(out_clean.strip()) == 0,
        })
        print(f"[{pid}] {dt:.1f}s rep={results[-1]['repetition']} "
              f"lang={'?' if results[-1]['lang_match'] is None else results[-1]['lang_match']}")

    # multi-turn: naive concat history (documents CURRENT behavior honestly)
    mt = []
    for mid, lang, turns in MULTI_TURN:
        hist = ""
        for i, t in enumerate(turns):
            ctx = hist + t + " "
            out, gids = gen(model, tok, ctx, cfg, max_new=32)
            hist += t + " " + out.strip() + " "
            mt.append({"seq": mid, "turn": i + 1, "prompt": t,
                       "output": out.strip(), "lang": lang})
        print(f"[mt:{mid}] done")

    # aggregates
    def agg(rs):
        n = len(rs)
        lm = [r for r in rs if r["lang_match"] is not None]
        return {
            "n": n,
            "avg_latency_s": round(sum(r["latency_s"] for r in rs) / n, 2),
            "avg_tok_per_s": round(sum(r["tok_per_s"] for r in rs) / n, 1),
            "avg_repetition": round(sum(r["repetition"] for r in rs) / n, 3),
            "eos_rate": round(sum(r["eos_hit"] for r in rs) / n, 3),
            "maxlen_rate": round(sum(r["max_len_hit"] for r in rs) / n, 3),
            "empty_rate": round(sum(r["empty_output"] for r in rs) / n, 3),
            "lang_match_rate": round(
                sum(r["lang_match"] for r in lm) / max(1, len(lm)), 3)
                if lm else None,
        }
    by_lang = {g: agg([r for r in results if r["lang"] == g])
               for g in ("en", "bn", "banglish", "mixed")}
    by_cat = {c: agg([r for r in results if r["category"] == c])
              for c in ("qa", "fact", "chat", "inst", "explain",
                        "math", "reason", "read", "know")}
    # keyword-hit correctness proxy for fact/qa/math with hints
    kw_hit = [r for r in results if r["expected_hint"]]
    kw_ok = sum(1 for r in kw_hit
                if r["expected_hint"].lower() in r["output"].lower())
    summary = {
        "benchmark": "neural_only_v2_100prompts",
        "version": "2.0",
        "checkpoint": args.ckpt, "checkpoint_sha": ckpt_sha,
        "params": model.count_parameters(),
        "ckpt_epoch": ck.get("epoch"), "ckpt_step": ck.get("step"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "gen_params": {"max_new": 48, "temp": 0.8, "top_k": 50,
                       "top_p": 0.9, "rep_penalty": 1.2},
        "overall": agg(results),
        "by_lang": by_lang, "by_category": by_cat,
        "keyword_hint_hit_rate": round(kw_ok / max(1, len(kw_hit)), 3),
        "keyword_hint_n": len(kw_hit),
        "multi_turn": mt,
        "results": results,
        "scoring_note": ("Automated metrics only: lang_match/script, "
                         "repetition, EOS, latency, keyword-hint presence. "
                         "Semantic correctness requires human review — "
                         "keyword hit is a LOWER-BOUND proxy, not proof."),
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    outp = os.path.join(OUT_DIR, "neural_benchmark_v2_" +
                        datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S") +
                        ".json")
    with open(outp, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1, ensure_ascii=False)
    print("\n==== OVERALL ====")
    print(json.dumps(summary["overall"], indent=1))
    print("by_lang:", json.dumps(by_lang, indent=1))
    print("kw_hit:", summary["keyword_hint_hit_rate"], f"({kw_ok}/{len(kw_hit)})")
    print("report:", outp)

if __name__ == "__main__":
    main()
