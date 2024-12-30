const mongoose = require('mongoose');

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
        type: Date,
        required: true,
        default: Date.now
    },
    expiryDate: {
        type: Date,
        required: true
    },
    isActive: {
        type: Boolean,
        default: true
    }
});

module.exports = mongoose.model('License', licenseSchema); 