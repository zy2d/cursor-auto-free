const crypto = require('crypto');

function getIV() {
    if (process.env.ENCRYPTION_IV) {
        return Buffer.from(process.env.ENCRYPTION_IV, 'hex');
    }
    return crypto.randomBytes(16);
}

function encryptLicenseKey(text) {
    const key = Buffer.from(process.env.ENCRYPTION_KEY, 'hex');
    const iv = getIV();
    const cipher = crypto.createCipheriv('aes-256-cbc', key, iv);
    let encrypted = cipher.update(text, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    return iv.toString('hex') + ':' + encrypted;
}

function decryptLicenseKey(encrypted) {
    const [ivHex, encryptedText] = encrypted.split(':');
    const key = Buffer.from(process.env.ENCRYPTION_KEY, 'hex');
    const iv = Buffer.from(ivHex, 'hex');
    const decipher = crypto.createDecipheriv('aes-256-cbc', key, iv);
    let decrypted = decipher.update(encryptedText, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    return decrypted;
}

function generateLicenseKey() {
    const randomBytes = crypto.randomBytes(16);
    const timestamp = Date.now().toString();
    const combined = randomBytes.toString('hex') + timestamp;
    const encrypted = encryptLicenseKey(combined);
    return encrypted;
}

function encryptResponse(data) {
    // 在开发模式下直接返回原始数据
    if (process.env.NODE_ENV === 'development') {
        return data;
    }

    // 生产模式下加密数据
    const jsonStr = JSON.stringify(data);
    const key = Buffer.from(process.env.ENCRYPTION_KEY, 'hex');
    const iv = getIV();
    const cipher = crypto.createCipheriv('aes-256-cbc', key, iv);
    let encrypted = cipher.update(jsonStr, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    return {
        encrypted_data: iv.toString('hex') + ':' + encrypted
    };
}

module.exports = {
    encryptLicenseKey,
    decryptLicenseKey,
    generateLicenseKey,
    encryptResponse
}; 