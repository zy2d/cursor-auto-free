require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const crypto = require('crypto');
const moment = require('moment');
const License = require('./models/License');

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Connect to MongoDB
mongoose.connect(process.env.MONGODB_URI)
    .then(() => console.log('Connected to MongoDB'))
    .catch(err => console.error('MongoDB connection error:', err));

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

        // Check if license already exists
        const existingLicense = await License.findOne({ licenseKey: license_key });
        if (existingLicense) {
            if (existingLicense.machineCode !== machine_code) {
                return res.status(400).json({
                    success: false,
                    message: '许可证已在其他设备上激活'
                });
            }
            if (!existingLicense.isActive) {
                return res.status(400).json({
                    success: false,
                    message: '许可证已被禁用'
                });
            }
        }

        // Create new license or update existing one
        const expiryDate = moment().add(1, 'year').toDate(); // 设置一年有效期
        const licenseData = {
            licenseKey: license_key,
            machineCode: machine_code,
            activationDate: activation_date || new Date(),
            expiryDate: expiryDate,
            isActive: true
        };

        if (existingLicense) {
            await License.updateOne({ licenseKey: license_key }, licenseData);
        } else {
            await License.create(licenseData);
        }

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