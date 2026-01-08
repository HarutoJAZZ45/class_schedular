import streamlit as st
import collections

# --- ロジック部分 (先ほどの関数と同じ) ---
def combine_classes(class_durations):
    """
    90分授業を45分×2に分割し、できるだけ異なる教科同士を組み合わせるロジック
    """
    # 1. コマを展開
    pool = []
    for subject, count in class_durations.items():
        pool.extend([subject] * (count * 2))
    
    counts = collections.Counter(pool)
    pairs = []
    
    # 2. ペア作成
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

# --- Webアプリの画面部分 ---
def main():
    st.set_page_config(page_title="時間割組み合わせ作成", layout="centered")
    
    st.title("📚 時間割組み合わせ作成ツール")
    st.write("各教科の90分授業のコマ数を入力すると、45分×2の最適な組み合わせを提案します。")
    
    st.divider()

    # 左サイドバーに入力フォームを配置
    st.sidebar.header("コマ数入力 (90分単位)")
    
    subjects = ["国語", "算数", "英語", "理科", "社会"]
    input_data = {}
    
    # 各教科の入力フォームを作成
    for subject in subjects:
        # number_input: 数値入力ボックス
        input_data[subject] = st.sidebar.number_input(
            f"{subject}のコマ数", 
            min_value=0, 
            max_value=20, 
            value=1, 
            step=1
        )

    # 計算実行ボタン
    if st.sidebar.button("組み合わせを作成する"):
        
        # 合計チェック
        if sum(input_data.values()) == 0:
            st.warning("少なくとも1つの教科に1以上のコマ数を入力してください。")
        else:
            # ロジック実行
            results = combine_classes(input_data)
            pair_counts = collections.Counter(results)
            
            # 結果表示エリア
            st.subheader("📝 作成結果")
            
            # データの整形（見やすく表示するため）
            display_data = []
            same_subject_alert = False
            
            for pair, count in pair_counts.items():
                subject1, subject2 = pair
                is_same = subject1 == subject2
                
                if is_same:
                    same_subject_alert = True
                    pair_str = f"⚠️ {subject1} ＋ {subject2}"
                else:
                    pair_str = f"{subject1} ＋ {subject2}"
                
                display_data.append({
                    "組み合わせ内容": pair_str,
                    "コマ数 (90分枠)": count,
                    "備考": "同じ教科のペア" if is_same else "OK"
                })
            
            # DataFrameとしてテーブル表示
            st.table(display_data)
            
            # メッセージ
            if same_subject_alert:
                st.info("※ ⚠️がついている箇所は、他の教科の残数が足りず、同じ教科同士のペアになっています。")
            else:
                st.success("すべてのコマが異なる教科とうまく組み合わされました！")

if __name__ == "__main__":
    main()
