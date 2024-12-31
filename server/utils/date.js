const moment = require('moment');
require('moment-timezone');

// 设置默认时区为中国时区
moment.tz.setDefault('Asia/Shanghai');

/**
 * 获取格式化的中国时区时间
 * @param {Date|String|Number} date - 日期输入
 * @param {String} format - 格式化模板，默认 'YYYY-MM-DD HH:mm:ss'
 * @returns {String} 格式化后的时间字符串
 */
const formatChinaTime = (date, format = 'YYYY-MM-DD HH:mm:ss') => {
  return moment(date).format(format);
};

/**
 * 获取当前中国时区的时间
 * @returns {moment} moment对象
 */
const getNowChinaTime = () => {
  return moment();
};

const getNowChinaTimeString = () => {
  return formatChinaTime(getNowChinaTime());
};

module.exports = {
  formatChinaTime,
  getNowChinaTime,
  getNowChinaTimeString,
  moment // 导出配置好时区的 moment 实例
};