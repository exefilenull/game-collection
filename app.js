const express = require('express');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const Game = require('./models/game');
const path = require('path');
const { MongoClient } = require("mongodb");


const app = express();
const port = 3000;

const uri = "mongodb://localhost:27017";
const client = new MongoClient(uri);
const dbName = "gamesoft";

// DB接続
mongoose.connect('mongodb://localhost:27017/gamesoft', { useNewUrlParser: true, useUnifiedTopology: true });

// ミドルウェア
app.use(bodyParser.urlencoded({ extended: false }));
app.use(express.static(path.join(__dirname, 'public')));

// テンプレートエンジン設定
app.set('view engine', 'ejs');

app.get("/api/collection-data", async (req, res) => {
    try {
        await client.connect();
        const db = client.db(dbName);
        
        // 大分類ごとのコレクション
        const collections = {
          任天堂: "1_nintendo",
          SNK: "2_snk",
          NEC: "3_nec",
          エポック: "4_epoch",
          Microsoft: "5_microsoft",
          BANDAI: "6_bandai",
          SEGA: "7_sega",
          SIE: "8_sie",
          Panasonic: "9_panasonic"
        };
        
        const result = {};

        for (const [category, collectionName] of Object.entries(collections)) {
      const platforms = await db.collection(collectionName).distinct("hard_title");

      for (const platform of platforms) {
      // category が未定義の場合、初期化する
        if (!result[category]) {
          result[category] = {};
        }
        
        // platform が未定義の場合、初期化する
        if (!result[category][platform]) {
          result[category][platform] = {};  // 空のオブジェクトで初期化
        }
        
        const totalGames = await db.collection(collectionName).countDocuments({ hard_title: platform , dont_collect: "false"});
        // 新品用のパラメータ
        const collectedGamesNew = await db.collection(collectionName).countDocuments({ 
            hard_title: platform,
            collected_new: "true"
        });
        // 中古用のパラメータ
        const collectedGamesOld = await db.collection(collectionName).countDocuments({ 
            hard_title: platform,
            collected_old: "true"
        });

        result[category][platform]['collection'] = collectionName;
        result[category][platform]['rateNew'] = Math.round((collectedGamesNew / totalGames) * 10000) / 100 || 0;
        result[category][platform]['rateOld'] = Math.round((collectedGamesOld / totalGames) * 10000) / 100 || 0;
        result[category][platform]['total'] = totalGames;
        result[category][platform]['collectedNew'] =  collectedGamesNew;
        result[category][platform]['collectedOld'] =  collectedGamesOld;
        
      }
    }

    res.json(result);
  } catch (err) {
    console.error(err);
    res.status(500).send("データ取得エラー");
  } finally {
    await client.close();
  }
});



// 各カテゴリの全体収集率を計算
//for (let category in gameCollection) {
//    let totalCollected = 0;
//    let totalGames = 0;
//    for (let platform in gameCollection[category].platforms) {
//        totalCollected += gameCollection[category].platforms[platform].collected;
//        totalGames += gameCollection[category].platforms[platform].total;
//    }
//    gameCollection[category].collected = totalCollected;
//    gameCollection[category].total = totalGames;
//}

//app.get("/game/:platform", (req, res) => {
//    res.render("game", { collectionData: gameCollection });
//});

app.get("/game/:platform", async (req, res) => {
    try {
        const platform = req.params.platform;
        await client.connect();
        const db = client.db(dbName);
        
        // 大分類ごとのコレクション
        const collections = [
            "1_nintendo", "2_snk", "3_nec", "4_epoch", "5_microsoft", 
            "6_bandai", "7_sega", "8_sie", "9_panasonic"
        ];
        
        let games = [];
        
        // 全コレクションから `hard_title` が `platform` に一致するゲームを取得
        for (const collectionName of collections) {
            const matchedGames = await db.collection(collectionName).find({ hard_title: platform }).toArray();
            games = games.concat(matchedGames);
        }
        
        // 収集率を計算する関数
        function calculateCollectionRate(games) {
          if (!games || games.length === 0) {
            return 0; // ゲームがない場合は 0% を返す
          }
          const collectedGames = games.filter(game => game.status === '収集済み').length;
          return ((collectedGames / games.length) * 100).toFixed(2); // 小数点2桁で返す
        }

        
        // 収集率の計算
        const collectionRate = calculateCollectionRate(games);

        res.render("game", { platform, games, collectionRate });
    } catch (err) {
        console.error(err);
        res.status(500).send("データ取得エラー");
    } finally {
        await client.close();
    }
});

app.get("/", (req, res) => {
    //res.render("index", { collectionData: gameCollection });
    res.render("index");
});

// ゲームの収集状況を更新
app.post('/game/:id', async (req, res) => {
  const gameId = req.params.id;
  const newStatus = req.body.status ? '収集済み' : '未収集';

  // 収集状況を更新
  await Game.findByIdAndUpdate(gameId, { status: newStatus });

  // 更新後、詳細ページにリダイレクト
  const game = await Game.findById(gameId);
  res.redirect(`/game/${game.platform}`);
});

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});