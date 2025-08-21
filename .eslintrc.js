module.exports = {
  root: true,
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  extends: [
    'eslint:recommended',
    '@vue/eslint-config-typescript',
    '@vue/eslint-config-prettier',
  ],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
  },
  rules: {
    // 代码风格规范
    'indent': ['error', 2],
    'quotes': ['error', 'single'],
    'semi': ['error', 'always'],
    'comma-dangle': ['error', 'always-multiline'],
    
    // 命名规范
    'camelcase': 'error',
    'no-underscore-dangle': 'error',
    
    // 最佳实践
    'no-console': 'warn',
    'no-debugger': 'error',
    'no-unused-vars': 'warn',
    'prefer-const': 'error',
    
    // Vue特定规范
    'vue/component-name-in-template-casing': ['error', 'PascalCase'],
    'vue/component-definition-name-casing': ['error', 'PascalCase'],
    'vue/multi-word-component-names': 'error',
    'vue/no-unused-components': 'warn',
    'vue/require-default-prop': 'error',
  },
  overrides: [
    {
      files: ['wechat-miniprogram/**/*.js'],
      rules: {
        // 微信小程序特定规范
        'no-console': 'off', // 小程序开发中可能需要console
        'no-undef': 'off', // 小程序全局变量
      },
    },
  ],
};
