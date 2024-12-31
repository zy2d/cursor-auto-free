const mongoose = require('mongoose');
const { getNowChinaTimeString } = require('../utils/date');
const licenseSchema = new mongoose.Schema({
    licenseKey: {
        type: String,
        required: true,
        unique: true
    },
    machineCode: {
        type: String,
        required: true
    },
    activationDate: {
        type: String,
        required: true,
        default: getNowChinaTimeString
    },
    expiryDate: {
        type: String,
        required: true
    },
    isActive: {
        type: Boolean,
        default: true
    },
    maxUsageCount: {
        type: Number,
        required: true,
        default: process.env.MAX_USAGE_COUNT || 10  // 默认允许使用100次
    },
    currentUsageCount: {
        type: Number,
        default: 0
    }
});

module.exports = mongoose.model('License', licenseSchema); 