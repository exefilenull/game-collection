// scripts/data-store.js
//
// DataStoreModule: 全カテゴリJSONの取得・GitHubへの保存・HTMLエスケープを提供する
// 共有ロジックモジュール。
// hardware_detail.html のインライン実装(jsonFiles配列 / saveToGitHub関数 /
// escapeHtml関数)を移動したもので、duplicate-game-cleanup spec からも
// 利用される前提のインターフェースを持つ(design.md 参照)。
//
// このモジュールは DOM 操作を行わず、ページ固有の状態(currentGames等)を
// 保持しない(design.md Invariants)。
(function (global) {
    'use strict';

    // 全カテゴリJSONファイルのパス一覧(hardware_detail.htmlの既存実装と同一)
    var CATEGORY_JSON_FILES = [
        'data/1_nintendo.json',
        'data/2_snk.json',
        'data/3_nec.json',
        'data/4_epoch.json',
        'data/5_microsoft.json',
        'data/6_bandai.json',
        'data/7_sega.json',
        'data/8_sie.json',
        'data/9_panasonic.json',
        'data/10_casio.json',
        'data/11_ascii.json',
        'data/12_tomy.json',
    ];

    /**
     * 全カテゴリJSON(12ファイル)を取得してパース済みの配列として返す。
     * ファイルの絞り込みオプションは持たない(design.md Preconditions)。
     *
     * @returns {Promise<Array<{category: string, hardware_name: Object}>>}
     */
    function fetchAllCategoryData() {
        return Promise.all(
            CATEGORY_JSON_FILES.map(function (file) {
                return fetch(file).then(function (res) {
                    return res.json();
                });
            })
        );
    }

    /**
     * 指定したパスに content を GitHub へコミットする。
     * netlify/functions/update.js を呼び出すラッパー。
     *
     * @param {string} path - 保存先のファイルパス(例: 'data/1_nintendo.json')
     * @param {string} content - 保存後の全内容(差分ではない)
     * @param {string} message - コミットメッセージ
     * @returns {Promise<{success: boolean, error?: string}>}
     */
    async function saveToGitHub(path, content, message) {
        try {
            const res = await fetch("/.netlify/functions/update", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    path: path,
                    content: content,
                    message: message,
                }),
            });

            const result = await res.json();
            if (result && result.success) {
                return { success: true };
            }
            return {
                success: false,
                error: (result && result.error) || "保存に失敗しました",
            };
        } catch (err) {
            return { success: false, error: err && err.message ? err.message : String(err) };
        }
    }

    /**
     * HTML特殊文字をエスケープする(XSS対策)。
     * hardware_detail.html の既存実装と同一のエスケープ結果を返す。
     *
     * @param {string} value
     * @returns {string}
     */
    function escapeHtml(value) {
        return String(value || '').replace(/[&<>"']/g, function (c) {
            return {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#39;',
            }[c];
        });
    }

    var DataStoreModule = {
        fetchAllCategoryData: fetchAllCategoryData,
        saveToGitHub: saveToGitHub,
        escapeHtml: escapeHtml,
    };

    // ブラウザ(グローバル公開) / Node(require経由のテスト等)の両方に対応
    global.DataStoreModule = DataStoreModule;
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = DataStoreModule;
    }
})(typeof window !== 'undefined' ? window : globalThis);
