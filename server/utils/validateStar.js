async function validateStar(username) {
  try {
    const response = await fetch(`https://api.github.com/users/${username}/starred`);
    
    if (response.ok) {
      const data = await response.json();
      const hasStarred = data.some(repo => repo.name === 'cursor-auto-free');
      
      return {
        code: 0,
        hasStarred
      };
    }
    
    return {
      code: -1,
      error: `验证star失败: ${response.status}`
    };

  } catch (error) {
    return {
      code: -1,
      error: `请求出错: ${error.message}`
    };
  }
}

module.exports = {
  validateStar
};
