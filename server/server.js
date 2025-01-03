require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const License = require('./models/License');
const LicenseKey = require('./models/LicenseKey');
const { formatChinaTime, getNowChinaTime, getNowChinaTimeString, moment } = require('./utils/date');
const { encryptLicenseKey, decryptLicenseKey, generateLicenseKey, encryptResponse } = require('./utils/encryption');
const { validateStar } = require('./utils/validateStar');
const UserGeneration = require('./models/UserGeneration');
const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// 添加访问日志中间件
app.use((req, res, next) => {
    const start = Date.now();
    res.on('finish', () => {
        const duration = Date.now() - start;
        console.log(`[${getNowChinaTimeString()}] ${req.method} ${req.originalUrl} - ${res.statusCode} - ${duration}ms`);
    });
    next();
});

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
const GENERATE_PATH = process.env.GENERATE_PATH || 'xx-zz-yy-dd';

// 在应用启动时输出生成路径（仅在控制台显示一次）
console.log('License generation path:', GENERATE_PATH);

// Generate license key endpoint
app.get(`/${GENERATE_PATH}`, async (req, res) => {
    try {
        const { username } = req.query;
        if (username !== 'ccj') {
            const starResult = await validateStar(username);
            if (starResult.code === -1 || starResult.hasStarred === false) {
                return res.status(200).json({
                    code: -1,
                    message: '不好意思，您还没有star我的项目，无法生成许可证'
                });
            }


            const userGeneration = await UserGeneration.findOne({ username: username });



            if (!userGeneration) {
                await UserGeneration.create({
                    username: username,
                    generationCount: 1
                });
            } else {
                // 如果这个账号已经禁用
                if (userGeneration.isDisabled) {
                    return res.status(200).json({
                        code: -1,
                        message: '不好意思，您的账号已被禁用，无法生成许可证'
                    });
                }

                // 如果这个月已经生成过许可证，则不能再次生成
                if (getNowChinaTime().month() === moment(userGeneration.lastGenerationTime).month()) {
                    return res.status(200).json({
                        code: -1,
                        message: '不好意思，这个月您已经生成过许可证，无法再次生成'
                    });
                }

                userGeneration.generationCount += 1;
                userGeneration.lastGenerationTime = getNowChinaTimeString();
                await userGeneration.save();
            }
        }


        const licenseKey = generateLicenseKey();

        await LicenseKey.create({
            licenseKey: licenseKey,
            isUsed: false
        });

        // 加密响应数据
        const responseData = {
            code: 0,
            data: licenseKey
        };

        return res.json(responseData);
    } catch (error) {
        console.error('生成许可证错误:', error);
        return res.status(500).json(encryptResponse({
            code: -1,
            message: '服务器错误'
        }));
    }
});

// Activation endpoint
app.post('/activate', async (req, res) => {
    try {
        const { license_key, machine_code, activation_date } = req.body;

        // Validate input
        if (!license_key || !machine_code) {
            return res.status(200).json(encryptResponse({
                code: -1,
                message: '许可证密钥和机器码是必需的'
            }));
        }

        // Validate license key format
        try {
            decryptLicenseKey(license_key);
        } catch (error) {
            return res.status(200).json(encryptResponse({
                code: -1,
                message: '无效的许可证密钥'
            }));
        }

        // 检查许可证是否存在于生成记录中
        const licenseKeyRecord = await LicenseKey.findOne({ licenseKey: license_key });
        if (!licenseKeyRecord) {
            return res.status(200).json(encryptResponse({
                code: -1,
                message: '无效的许可证密钥'
            }));
        }

        // 检查许可证是否已被使用
        if (licenseKeyRecord.isUsed) {
            return res.status(200).json(encryptResponse({
                code: -1,
                message: '此许可证密钥已被使用，不能重复激活'
            }));
        }

        // 检查许可证激活状态
        const existingLicense = await License.findOne({ licenseKey: license_key });
        if (existingLicense) {
            return res.status(200).json(encryptResponse({
                code: -1,
                message: '此许可证已被激活，不能重复使用'
            }));
        }

        // 更新过期时间计算，使用中国时区
        const expiryDate = formatChinaTime(getNowChinaTime().add(1, 'month'), 'YYYY-MM-DD');

        await License.create([{
            licenseKey: license_key,
            machineCode: machine_code,
            activationDate: activation_date ? activation_date : getNowChinaTimeString(),
            expiryDate: expiryDate,
            isActive: true,
            maxUsageCount: process.env.MAX_USAGE_COUNT || 10,
            currentUsageCount: 1
        }]);


        // 更新许可证密钥状态为已使用
        licenseKeyRecord.isUsed = true;
        await licenseKeyRecord.save();

        const responseData = {
            code: 0,
            message: '激活成功',
            data: {
                expiry_date: expiryDate
            }
        };

        return res.json(encryptResponse(responseData));
    } catch (error) {
        console.error('激活错误:', error);
        return res.status(500).json(encryptResponse({
            code: -1,
            message: '服务器错误'
        }));
    }
});

// Verification endpoint
app.post('/verify', async (req, res) => {
    try {
        const { license_key, machine_code } = req.body;

        // Validate input
        if (!license_key || !machine_code) {
            return res.status(200).json(encryptResponse({
                code: -1,
                message: '许可证密钥和机器码是必需的'
            }));
        }

        // Validate license key format
        try {
            decryptLicenseKey(license_key);
        } catch (error) {
            return res.status(200).json(encryptResponse({
                code: -1,
                message: '无效的许可证密钥'
            }));
        }

        // Find license
        const license = await License.findOne({ licenseKey: license_key });

        if (!license) {
            return res.status(200).json(encryptResponse({
                code: -1,
                message: '许可证不存在'
            }));
        }

        // Check machine code
        if (license.machineCode !== machine_code) {
            return res.status(200).json(encryptResponse({
                code: -1,
                message: '硬件信息不匹配'
            }));
        }

        // Check if license is active
        if (!license.isActive) {
            return res.status(200).json(encryptResponse({
                code: -1,
                message: '许可证已被禁用'
            }));
        }

        // 使用中国时区检查过期时间
        if (getNowChinaTime().isAfter(license.expiryDate)) {
            return res.status(200).json(encryptResponse({
                code: -1,
                message: '许可证已过期'
            }));
        }

        // 检查使用次数
        if (license.currentUsageCount >= license.maxUsageCount) {
            return res.status(200).json(encryptResponse({
                code: -1,
                message: '许可证使用次数已达到上限'
            }));
        }

        // 更新使用次数
        license.currentUsageCount += 1;
        await license.save();

        const responseData = {
            code: 0,
            data: {
                message: '许可证有效',
                expiry_date: formatChinaTime(license.expiryDate, 'YYYY-MM-DD'),
                usage_count: {
                    current: license.currentUsageCount,
                    max: license.maxUsageCount
                }
            }
        };

        return res.json(encryptResponse(responseData));
    } catch (error) {
        console.error('验证错误:', error);
        return res.status(500).json(encryptResponse({
            code: -1,
            message: '服务器错误'
        }));
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
}); 