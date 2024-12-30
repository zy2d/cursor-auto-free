require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const crypto = require('crypto');
const moment = require('moment');
const License = require('./models/License');
const LicenseKey = require('./models/LicenseKey');

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Encryption functions
function getIV() {
    // 如果需要固定 IV（不推荐），可以从环境变量获取
    if (process.env.ENCRYPTION_IV) {
        return Buffer.from(process.env.ENCRYPTION_IV, 'hex');
    }
    // 否则生成随机 IV（更安全，但需要存储）
    return crypto.randomBytes(16);
}

function encryptLicenseKey(text) {
    const key = Buffer.from(process.env.ENCRYPTION_KEY, 'hex');
    const iv = getIV();
    const cipher = crypto.createCipheriv('aes-256-cbc', key, iv);
    let encrypted = cipher.update(text, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    // 将 IV 附加到加密文本中，以便解密时使用
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
    // 由于加密后的字符串现在包含 IV，我们需要使用完整的字符串
    return encrypted;
}

// Connect to MongoDB
mongoose.connect(process.env.MONGODB_URI, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
    serverSelectionTimeoutMS: 5000, // 超时时间
    socketTimeoutMS: 45000, // Socket 超时
    family: 4, // 强制使用 IPv4
})
.then(() => console.log('Connected to MongoDB'))
.catch(err => {
    console.error('MongoDB connection error:', err);
    process.exit(1); // 如果连接失败，终止程序
});

// 添加连接错误处理
mongoose.connection.on('error', err => {
    console.error('MongoDB connection error:', err);
});

mongoose.connection.on('disconnected', () => {
    console.log('MongoDB disconnected');
});

// 定义一个复杂的路径，可以放在环境变量中
const GENERATE_PATH = process.env.GENERATE_PATH || crypto.randomBytes(16).toString('hex');

// 在应用启动时输出生成路径（仅在控制台显示一次）
console.log('License generation path:', GENERATE_PATH);

// Generate license key endpoint
app.post(`/${GENERATE_PATH}`, async (req, res) => {
    try {
        const licenseKey = generateLicenseKey();
        
        // 保存生成的许可证记录
        await LicenseKey.create({
            licenseKey: licenseKey,
            isUsed: false
        });

        return res.json({
            success: true,
            license_key: licenseKey
        });
    } catch (error) {
        console.error('生成许可证错误:', error);
        return res.status(500).json({
            success: false,
            message: '服务器错误'
        });
    }
});

// Activation endpoint
app.post('/activate', async (req, res) => {
    try {
        const { license_key, machine_code, activation_date } = req.body;

        // Validate input
        if (!license_key || !machine_code) {
            return res.status(400).json({
                success: false,
                message: '许可证密钥和机器码是必需的'
            });
        }

        // Validate license key format
        try {
            decryptLicenseKey(license_key);
        } catch (error) {
            return res.status(400).json({
                success: false,
                message: '无效的许可证密钥'
            });
        }

        // 检查许可证是否存在于生成记录中
        const licenseKeyRecord = await LicenseKey.findOne({ licenseKey: license_key });
        if (!licenseKeyRecord) {
            return res.status(400).json({
                success: false,
                message: '无效的许可证密钥'
            });
        }

        // 检查许可证是否已被使用
        if (licenseKeyRecord.isUsed) {
            return res.status(400).json({
                success: false,
                message: '此许可证密钥已被使用，不能重复激活'
            });
        }

        // 检查许可证激活状态
        const existingLicense = await License.findOne({ licenseKey: license_key });
        if (existingLicense) {
            return res.status(400).json({
                success: false,
                message: '此许可证已被激活，不能重复使用'
            });
        }

        // 创建新的许可证并标记许可证密钥为已使用
        const expiryDate = moment().add(1, 'month').toDate();
       

        // 更新许可证密钥状态为已使用
        licenseKeyRecord.isUsed = true;
        await licenseKeyRecord.save();

        return res.json({
            success: true,
            message: '激活成功',
            expiry_date: expiryDate.toISOString().split('T')[0]
        });
    } catch (error) {
        console.error('激活错误:', error);
        return res.status(500).json({
            success: false,
            message: '服务器错误'
        });
    }
});

// Verification endpoint
app.post('/verify', async (req, res) => {
    try {
        const { license_key, machine_code } = req.body;

        // Validate input
        if (!license_key || !machine_code) {
            return res.status(400).json({
                success: false,
                message: '许可证密钥和机器码是必需的'
            });
        }

        // Validate license key format
        try {
            decryptLicenseKey(license_key);
        } catch (error) {
            return res.status(400).json({
                success: false,
                message: '无效的许可证密钥'
            });
        }

        // Find license
        const license = await License.findOne({ licenseKey: license_key });
        
        if (!license) {
            return res.status(404).json({
                success: false,
                message: '许可证不存在'
            });
        }

        // Check machine code
        if (license.machineCode !== machine_code) {
            return res.status(400).json({
                success: false,
                message: '硬件信息不匹配'
            });
        }

        // Check if license is active
        if (!license.isActive) {
            return res.status(400).json({
                success: false,
                message: '许可证已被禁用'
            });
        }

        // Check expiry
        if (moment().isAfter(license.expiryDate)) {
            return res.status(400).json({
                success: false,
                message: '许可证已过期'
            });
        }

        return res.json({
            success: true,
            message: '许可证有效',
            expiry_date: license.expiryDate.toISOString().split('T')[0]
        });
    } catch (error) {
        console.error('验证错误:', error);
        return res.status(500).json({
            success: false,
            message: '服务器错误'
        });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
}); 