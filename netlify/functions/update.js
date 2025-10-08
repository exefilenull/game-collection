// netlify/functions/update.js
import fetch from "node-fetch";

export const handler = async (event) => {
  try {
    const { path, content, message } = JSON.parse(event.body);

    const owner = process.env.REPO_OWNER;
    const repo = process.env.REPO_NAME;
    const token = process.env.GITHUB_TOKEN;

    // GitHubのAPIエンドポイント
    const apiUrl = `https://api.github.com/repos/${owner}/${repo}/contents/${path}`;

    // 現在のSHAを取得（上書き時に必要）
    const current = await fetch(apiUrl, {
      headers: { Authorization: `token ${token}` },
    }).then(res => res.json());

    // ファイル内容をBase64でエンコード
    const encodedContent = Buffer.from(content).toString("base64");

    // 更新リクエストを送信
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
      body: JSON.stringify({ success: true, result }),
    };
  } catch (err) {
    return { statusCode: 500, body: JSON.stringify({ error: err.message }) };
  }
};