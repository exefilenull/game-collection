// MongoDB Atlas Data API 設定
const MONGO_API_URL = 'https://data.mongodb-api.com/app/あなたのアプリID/endpoint/data/v1/action/find';
const API_KEY = 'あなたのAPIキー';
const DATABASE_NAME = 'game_collection';
const COLLECTION_NAME = '5_microsoft';

// MongoDBからデータ取得
async function fetchGameData() {
  try {
    const response = await fetch(MONGO_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Request-Headers': '*',
        'api-key': API_KEY,
      },
      body: JSON.stringify({
        dataSource: 'Cluster0',
        database: DATABASE_NAME,
        collection: COLLECTION_NAME,
      }),
    });

    if (!response.ok) {
      throw new Error(`データ取得に失敗: ${response.statusText}`);
    }

    const result = await response.json();
    return result.documents; // MongoDBのドキュメント
  } catch (error) {
    console.error('データ取得エラー:', error);
  }
}

// 収集率計算と表示
async function displayGameCollection() {
  const data = await fetchGameData();
  if (!data) return;

  const totalGames = data.length;
  const collectedGames = data.filter(game => game.collected_new === 1).length;
  const collectionRate = ((collectedGames / totalGames) * 100).toFixed(2);

  const chartContainer = document.getElementById('chart-container');
  chartContainer.innerHTML = `
    <p>総ゲーム数: ${totalGames}</p>
    <p>収集済み: ${collectedGames}</p>
    <p>収集率: ${collectionRate}%</p>
  `;
}

displayGameCollection();
