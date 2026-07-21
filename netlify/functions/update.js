// netlify/functions/update.js
//
// このFunctionはGitHub Pages(exefilenull.github.io)から絶対URLでクロス
// オリジン呼び出しされるため、CORSヘッダーとpreflight(OPTIONS)対応が必要。
const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "https://exefilenull.github.io",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};

export const handler = async (event) => {
  // ブラウザが送るCORS preflightリクエストにはボディが無いため、
  // JSON.parse等を行う前にここで処理して返す。
  if (event.httpMethod === "OPTIONS") {
    return {
      statusCode: 204,
      headers: CORS_HEADERS,
      body: "",
    };
  }

  try {
    const { path, content, message } = JSON.parse(event.body);

    const owner = process.env.REPO_OWNER;
    const repo = process.env.REPO_NAME;
    const token = process.env.GITHUB_TOKEN;

    if (!owner || !repo || !token) {
      throw new Error(
        `Netlifyの環境変数が未設定です(REPO_OWNER=${owner ? "set" : "missing"}, REPO_NAME=${repo ? "set" : "missing"}, GITHUB_TOKEN=${token ? "set" : "missing"})`
      );
    }

    const apiUrl = `https://api.github.com/repos/${owner}/${repo}/contents/${path}`;

    // 現在のSHAを取得
    const currentRes = await fetch(apiUrl, {
      headers: { Authorization: `token ${token}` },
    });
    const current = await currentRes.json();

    if (!current.sha) {
      throw new Error(
        `対象ファイルが見つかりません: ${path} (GitHub API status=${currentRes.status}, message=${(current && current.message) || "unknown"})`
      );
    }

    // Base64エンコード
    const encodedContent = Buffer.from(content).toString("base64");

    // PUTリクエストでGitHubに保存
    const response = await fetch(apiUrl, {
      method: "PUT",
      headers: {
        "Authorization": `token ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: message || "Update JSON via web UI",
        content: encodedContent,
        sha: current.sha,
      }),
    });

    const result = await response.json();
    return {
      statusCode: 200,
      headers: CORS_HEADERS,
      body: JSON.stringify({ success: true, result }),
    };
  } catch (err) {
    return {
      statusCode: 500,
      headers: CORS_HEADERS,
      body: JSON.stringify({ error: err.message }),
    };
  }
};
