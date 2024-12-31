const mongoose = require('mongoose');
const { getNowChinaTimeString } = require('../utils/date');

const licenseKeySchema = new mongoose.Schema({
    licenseKey: {
        type: String,
        required: true,
        unique: true
    },
    isUsed: {
        type: Boolean,
        default: false
    },
    generatedAt: {
        type: String,
        default() {
            return getNowChinaTimeString();
        }
    }
});

module.exports = mongoose.model('LicenseKey', licenseKeySchema); 