import streamlit as st
import collections

# --- ページ設定 (最初に行う必要があります) ---
st.set_page_config(
    page_title="Class Pair",
    page_icon="🧩",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- カスタムCSS (デザインの核心) ---
# Streamlit標準の見た目を上書きして、モダンなWebアプリ風にします
st.markdown("""
<style>
    /* 全体のフォントと背景 */
    .stApp {
        background-color: #FAFAFA; /* ほんのりグレーで目に優しく */
        font-family: "Helvetica Neue", Arial, "Hiragino Kaku Gothic ProN", "Hiragino Sans", Meiryo, sans-serif;
    }
    
    /* ヘッダーの余白調整 */
    .block-container {
        padding-top: 3rem;
        padding-bottom: 5rem;
        max_width: 600px; /* スマホで見やすい幅に制限 */
    }

    /* タイトルデザイン */
    h1 {
        font-weight: 800 !important;
        color: #333;
        font-size: 2.2rem !important;
        margin-bottom: 0.5rem !important;
        text-align: center;
    }
    p {
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }

    /* 入力エリアのカード化 */
    .input-card {
        background: white;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
        margin-bottom: 20px;
    }

    /* ボタンのカスタム */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 15px 0;
        font-size: 1.1rem;
        font-weight: bold;
        border-radius: 12px;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(118, 75, 162, 0.3);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(118, 75, 162, 0.4);
        color: white;
    }

    /* 結果カードのデザイン */
    .result-card {
        background: white;
        padding: 15px 20px;
        border-radius: 12px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
        border-left: 6px solid #e2e8f0;
        transition: transform 0.2s;
    }
    .result-card:hover {
        transform: scale(1.02);
    }
    .result-card.good {
        border-left-color: #48bb78; /* Green */
    }
    .result-card.bad {
        border-left-color: #f56565; /* Red */
    }
    
    .subject-name {
        font-weight: bold;
        color: #2d3748;
        font-size: 1.05rem;
    }
    .count-badge {
        background: #edf2f7;
        color: #4a5568;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    /* Streamlitの不要な要素を隠す */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- ロジック (変更なし) ---
def combine_classes(class_durations):
    pool = []
    for subject, count in class_durations.items():
        pool.extend([subject] * (count * 2))
    counts = collections.Counter(pool)
    pairs = []
    while sum(counts.values()) > 0:
        sorted_subjects = counts.most_common()
        primary = sorted_subjects[0][0]
        counts[primary] -= 1
        secondary = None
        if len(sorted_subjects) > 1 and sorted_subjects[1][1] > 0:
            secondary = sorted_subjects[1][0]
            counts[secondary] -= 1
        else:
            if counts[primary] > 0:
                 secondary = primary
                 counts[primary] -= 1
            else:
                 secondary = "空き時間"
        pair = tuple(sorted([primary, secondary]))
        pairs.append(pair)
    return pairs

# --- メイン画面 ---
def main():
    # タイトル部分
    st.markdown("<h1>Class Pair</h1>", unsafe_allow_html=True)
    st.markdown("<p>90分授業を45分×2に最適化</p>", unsafe_allow_html=True)

    # 入力セクション（カード風デザインの中に配置）
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    
    subjects = ["国語", "算数", "英語", "理科", "社会"]
    input_data = {}
    
    # スマホで見やすいように 2列カラム で入力を配置
    cols = st.columns(2)
    for i, subject in enumerate(subjects):
        with cols[i % 2]:
            input_data[subject] = st.number_input(
                f"{subject}", 
                min_value=0, max_value=10, value=1 if i < 3 else 0, 
                key=subject
            )
    
    st.markdown('</div>', unsafe_allow_html=True)

    # アクションボタン（CSSで大きくデザイン済み）
    if st.button("組み合わせを生成"):
        if sum(input_data.values()) == 0:
            st.error("教科のコマ数を入力してください")
        else:
            results = combine_classes(input_data)
            pair_counts = collections.Counter(results)
            
            # 結果表示エリア
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 概要を表示
            total_slots = len(results)
            st.markdown(f"<p style='text-align:left; font-weight:bold; color:#a0aec0; margin-bottom:10px;'>TOTAL: {total_slots} 枠</p>", unsafe_allow_html=True)

            for pair, count in pair_counts.items():
                subject1, subject2 = pair
                is_same = subject1 == subject2
                
                # クラス分け（CSS用）
                card_class = "bad" if is_same else "good"
                icon = "⚠️" if is_same else "✨"
                
                # HTMLカード描画
                st.markdown(f"""
                <div class="result-card {card_class}">
                    <div class="subject-name">
                        {subject1} <span style="color:#cbd5e0; margin:0 8px;">|</span> {subject2}
                    </div>
                    <div class="count-badge">
                        × {count}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # フィードバックメッセージ
            if any(p[0] == p[1] for p in pair_counts.keys()):
                st.markdown("<p style='font-size:0.8rem; color:#f56565; margin-top:20px;'>※ 一部、同じ教科のペアが含まれています</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
