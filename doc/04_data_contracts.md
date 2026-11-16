# データ契約（v0.1案）

## 共通規約
UTF-8 JSON。内部単位はm、角度はdegree。平面座標はUnityのx,z、高さはy。原点は広場南西、範囲x∈[0,20], z∈[0,10]。yaw=0は+z、yaw=90は+x。方角を画面の左右と混同しない。「右」は初期版では固定俯瞰図の+xとし、画面に方位を表示する。カメラ基準の指定は後続機能。
IDは削除後も再利用しない。数値は有限値のみ。辞書の順序に依存しない。schema_version、feature_set_version、catalog_versionを記録する。

## 主要データ
| 型 | 必須情報 |
|---|---|
| SceneState | session_id, scene_revision, boundary, entrances, forbidden_regions, objects, catalog_version |
| ObjectState | object_id, type_id, position_m{x,y,z}, yaw_deg, dimensions_m{x,y,z}, footprint_local_xz, attributes, roles |
| EditIntent | action, target_selector, resolved_target_ids, relation, requested_scope, preference_evidence, ambiguities |
| PreferenceEvidence | feature_id, polarity(-1/0/+1), source_span, evidence_type, scope, related_proposal_id |
| FeatureDefinition | feature_id, definition_version, description, dependencies, calculator_id, parameters, normalization, empty_case |
| FeatureSnapshot | feature_set_version, values_by_id, validity_by_id, diagnostics |
| PreferenceState | learner_id, learner_version, weights_by_id, feature_set_version, parameters, evidence_history |
| Candidate | proposal_id, base_scene_revision, parent_proposal_id, scene, intent_checks, geometry_checks, features, score_components |
| Feedback | feedback_id, proposal_id, accept/reject/revise, text, selected_ids, timestamp |

footprint_local_xzは物体中心を原点とする多角形。ベンチの前面はlocal +z。境界・footprintへの変換を共通テストする。
requested_scopeはsingle/group/all/global。対象不明をallとして補完しない。複合指示はoperations配列で表現し、初期版は全体を一つのトランザクションとして成功または失敗させる。
PreferenceEvidenceのscopeはcurrent_edit / general / uncertain。LLMの分類結果は真値ではなく解析結果として保存する。

## APIの初期案
| API | 用途 |
|---|---|
| GET /health | 稼働確認 |
| POST /sessions | 初期SceneState・設定からセッション作成 |
| POST /sessions/{id}/proposals | 発話・選択ID・基準版・修正元から提案 |
| POST /sessions/{id}/feedback | 採用／却下。冪等な確定処理 |
| GET /sessions/{id}/state | 確定配置・処理状態を再同期 |
| POST /sessions/{id}/reset | 新しい試行として初期化。過去ログを消さない |

修正はproposalsへparent_proposal_idを渡す。返却statusはproposed / clarification_required / failed。採用応答は新しいscene_revisionと学習監査情報を含む。タイムアウト後はstateを取得し、成功した採用を再実行しない。

## ログ
JSONLのイベント列と、初期設定・シーン・特徴定義のスナップショットを保存する。全イベントにrun_id, session_id, event_id, request_id, UTC timestamp, scene_revisionを付ける。
イベント種: session_started, utterance_received, interpretation_completed, targets_resolved, candidates_generated, proposal_presented, feedback_received, scene_committed, learning_updated, clarification, failure, session_finished。
候補ごとの制約判定、提示前後の特徴、重み、更新マスク、根拠span、探索seed、候補数、処理時間、モデル設定、プロンプト版、利用量を保存。API応答の機密情報は除去する。
システムが読めるログと、真の重み・ペルソナを含む評価専用ログを分離する。学習処理へ評価専用ログを渡さない。

## 保持根拠・反復分析用の追加契約案
PreferenceEvidenceにevidence_id、utterance_id、episode_id、scope、polarity、source_span、対象ID・関係、作成版、状態(active/superseded/consumed/expired)、関連提案IDを追加する。採用時には使用した根拠IDと採用イベントIDの対応を保存する。根拠だけの入力はknowledge_recordedとして返し、提案なし・scene_revision不変・重み不変とする（このstatus追加は暫定API案）。Evidence履歴の保存と、学習器が参照可能な有効根拠は分離する。
操作ログにはepisode_id、retry_of/correction_of、対象ID、操作・関係、前後配置・特徴、達成判定、採否、根拠ID、システム選択と利用者要求の区別を保存する。評価専用ラベル・真の重みは編集系の入力から分離する。
