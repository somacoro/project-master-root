# システム構成（暫定実装案）

## モジュール
| モジュール | 責務 |
|---|---|
| Unity SceneAdapter | GameObjectと共通SceneStateの相互変換 |
| Unity InteractionUI | テキスト、選択、プレビュー、採否、視点操作 |
| Python SessionService | セッション、版、提案、採用の整合性管理 |
| LanguageInterpreter | 操作・対象条件・好みの根拠を構造化 |
| TargetResolver | シーン内の実在IDへ条件を解決 |
| CandidateGenerator | 操作と解釈から複数候補を生成 |
| GeometryValidator | footprint、敷地、禁止領域などの検証 |
| FeatureRegistry / FeatureEvaluator | IDと版に基づく特徴定義・計算 |
| CandidateRanker | 指示適合・効用・変更量による順位付け |
| PreferenceLearner | 根拠を選び、重みを更新 |
| ExperimentRunner / UserSimulator | 固定シナリオ、数理・LLM利用者 |
| EventLogger | 再現・分析用の不変イベントを保存 |

## 通信と状態
同一PCのlocalhost HTTP/JSONを初期案とする。具体的なWebフレームワーク、Python版、依存ライブラリは実装開始時に互換性を確認して固定する。
Pythonはセッションの確定SceneState・選好状態を管理する。Unityは起動時にシーンを取り込み、以後は承認された版を描画する。Unity側で手動変更した場合は新しい状態として明示的に再同期し、古い提案を無効化する。
各リクエストにrequest_idとbase_scene_revisionを付与。同一セッションの変更処理を直列化し、二重採用で重みが二重更新されないようにする。

## C#とPythonの境界
PythonはUnityのColliderを直接参照しない。全判定に必要なfootprint・高さ・向き・役割を送る。初期版の正規の幾何判定は共通データに対してPythonが実施し、Unity表示側が同じ寸法を使う。将来Unityの物理判定を追加する場合は判定バージョンと結果を記録し、食い違いを隠さない。
研究用の特徴計算をUnityとPythonで別々に実装しない。ヘッドレス実験でも同じ特徴・探索・学習処理を使う。

## 差し替え境界
- LLMProvider: structured request→validated response。モデル名、温度、制限、再試行を設定化。
- Planner: SceneState + EditIntent + PreferenceState→Candidate[]。
- Learner: Evidence + before/after + prior state→updated state + audit。
- UserSimulator: 観察可能な提案情報→accept/reject/revise/finish。
- FeatureEvaluator: SceneState + FeatureDefinition→value + validity + diagnostics。

## エラー
schema_invalid、target_not_found、target_ambiguous、infeasible、timeout、provider_error、stale_revisionを区別する。失敗時は確定配置・重みを保持し、理由付きイベントを出す。再試行回数は有限。既に採用されたrequest_idの再送には同じ結果を返す。
