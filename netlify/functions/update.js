// netlify/functions/update.js
export const handler = async (event) => {
  try {
    const { path, content, message } = JSON.parse(event.body);

    const owner = process.env.REPO_OWNER;
    const repo = process.env.REPO_NAME;
    const token = process.env.GITHUB_TOKEN;

    const apiUrl = `https://api.github.com/repos/${owner}/${repo}/contents/${path}`;

    // 現在のSHAを取得
    const current = await fetch(apiUrl, {
      headers: { Authorization: `token ${token}` },
    }).then(res => res.json());

    if (!current.sha) {
      throw new Error(`対象ファイルが見つかりません: ${path}`);
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
      body: JSON.stringify({ success: true, result }),
    };
  } catch (err) {
    return { statusCode: 500, body: JSON.stringify({ error: err.message }) };
  }
};
