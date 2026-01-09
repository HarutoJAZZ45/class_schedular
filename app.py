import streamlit as st
import collections
import math

# --- 1. ページ設定 (Wideモードで画面を広く使う) ---
st.set_page_config(
    page_title="Class Pair (PC)",
    page_icon="⌨️",
    layout="wide",  # 横幅いっぱいに使う
    initial_sidebar_state="collapsed"
)

# --- 2. CSS注入 (余白を削り、一画面に収める) ---
st.markdown("""
<style>
    /* 全体の余白を極限まで削る */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 1rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }
    
    /* タイトル周りをコンパクトに */
    h1 { font-size: 1.8rem !important; margin-bottom: 0 !important; }
    p { margin-bottom: 0.5rem !important; }

    /* 入力フォームの背景 */
    [data-testid="stForm"] {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #ddd;
    }

    /* 結果カードのデザイン（コンパクト版） */
    .result-box {
        background-color: white;
        border: 1px solid #eee;
        border-left: 4px solid #ddd;
        padding: 8px 12px;
        margin-bottom: 8px;
        border-radius: 4px;
        font-size: 0.95rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .result-box.ok { border-left-color: #00CC66; } /* 緑 */
    .result-box.ng { border-left-color: #FF3333; background-color: #fff5f5; } /* 赤 */
    
    .subject-text { font-weight: bold; color: #333; }
    .badge { 
        background: #eee; color: #555; 
        font-size: 0.8rem; padding: 2px 8px; border-radius: 10px; 
    }

    /* キーボード操作フォーカス時の視認性向上 */
    input:focus {
        background-color: #e8f0fe !important;
        border-color: #4285f4 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. ロジック ---
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

# --- 4. メイン画面構成 ---
def main():
    st.title("⌨️ Class Pair Optimizer")
    st.caption("Tabキーで移動、数値を入力し、最後にEnter(Ctrl+Enter)で実行")

    # 画面を左右に分割 (左:入力 1 : 右:結果 3 の比率)
    col_input, col_result = st.columns([1, 3], gap="large")

    # --- 左カラム：入力フォーム ---
    with col_input:
        # st.formを使うことで、エンターキーでのリロードを防ぎ、最後に一括送信できる
        with st.form(key="input_form"):
            st.markdown("##### 📝 Input (90min)")
            
            subjects = ["国語", "算数", "英語", "理科", "社会"]
            input_data = {}
            
            # 各入力欄
            for subject in subjects:
                input_data[subject] = st.number_input(
                    f"{subject}", 
                    min_value=0, max_value=20, value=1 if subject in ["国語", "算数"] else 0,
                    step=1
                )
            
            st.markdown("---")
            # Submitボタン（これがフォームのトリガー）
            submit_btn = st.form_submit_button("実行 (Enter)", type="primary")

    # --- 右カラム：結果表示 ---
    with col_result:
        if submit_btn:
            if sum(input_data.values()) == 0:
                st.warning("コマ数を入力してください。")
            else:
                results = combine_classes(input_data)
                pair_counts = collections.Counter(results)
                
                # ヘッダー情報
                st.markdown(f"##### 📊 Result (Total: {len(results)} pairs)")
                
                # 結果を「横並び」に展開して縦スクロールを防ぐ
                # 結果の個数に応じてカラム数を動的に決める（最大3列）
                n_results = len(pair_counts)
                n_cols = 3 if n_results > 6 else (2 if n_results > 3 else 1)
                
                # 結果表示用のカラムを作成
                result_columns = st.columns(n_cols)
                
                # 辞書アイテムをリスト化してインデックスアクセスできるようにする
                items = list(pair_counts.items())
                
                # 各カラムにデータを均等に分配して表示
                chunk_size = math.ceil(len(items) / n_cols)
                
                for i in range(n_cols):
                    with result_columns[i]:
                        start = i * chunk_size
                        end = start + chunk_size
                        for pair, count in items[start:end]:
                            subject1, subject2 = pair
                            is_same = subject1 == subject2
                            
                            status_class = "ng" if is_same else "ok"
                            
                            # シンプルなHTML表示
                            st.markdown(f"""
                            <div class="result-box {status_class}">
                                <span class="subject-text">{subject1} ＋ {subject2}</span>
                                <span class="badge">×{count}</span>
                            </div>
                            """, unsafe_allow_html=True)
                
                # 警告メッセージがあれば下部に控えめに表示
                if any(p[0] == p[1] for p in pair_counts.keys()):
                    st.error("⚠️ 同じ教科の組み合わせが含まれています")
        else:
            # 初期状態の案内
            st.info("👈 左側のフォームに数値を入力し、実行してください。")

if __name__ == "__main__":
    main()
