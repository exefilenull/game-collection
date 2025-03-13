const mongoose = require('mongoose');

const gameSchema = new mongoose.Schema({
  title: String,
  platform: String,
  status: { type: String, default: '未収集' }
});

const Game = mongoose.model('Game', gameSchema);
module.exports = Game;
