const mongoose = require('mongoose');
const { getNowChinaTimeString } = require('../utils/date');

const userGenerationSchema = new mongoose.Schema({
  username: {
    type: String,
    required: true,
    unique: true,
    index: true
  },
  lastGenerationTime: {
    type: String,
    default() {
      return getNowChinaTimeString();
    }
  },
  generationCount: {
    type: Number,
    default: 0
  },
  isDisabled: {
    type: Boolean,
    default: false
  },

}, {
  timestamps: true // 添加 createdAt 和 updatedAt 字段
});

// 创建索引以优化查询性能
userGenerationSchema.index({ username: 1 });

const UserGeneration = mongoose.model('UserGeneration', userGenerationSchema);

module.exports = UserGeneration; 