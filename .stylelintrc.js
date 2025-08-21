module.exports = {
  extends: [
    'stylelint-config-standard',
    'stylelint-config-standard-scss',
  ],
  plugins: [
    'stylelint-scss',
  ],
  rules: {
    // 强制使用预定义变量
    'declaration-property-value-allowed-list': null,
    
    // 颜色规范
    'color-hex-case': 'lower',
    'color-hex-length': 'short',
    'color-named': 'never',
    
    // 字体规范
    'font-family-name-quotes': 'always-where-required',
    'font-weight-notation': 'numeric',
    
    // 数值规范
    'number-leading-zero': 'always',
    'unit-case': 'lower',
    'unit-no-unknown': true,
    
    // 选择器规范
    'selector-class-pattern': '^[a-z]([a-z0-9-]+)?(__([a-z0-9]+-?)+)?(--([a-z0-9]+-?)+){0,2}$',
    'selector-id-pattern': '^[a-z]([a-z0-9-]+)?$',
    
    // 属性规范
    'property-case': 'lower',
    'property-no-vendor-prefix': true,
    'declaration-block-no-duplicate-properties': true,
    
    // 布局规范
    'declaration-block-trailing-semicolon': 'always',
    'declaration-colon-space-after': 'always',
    'declaration-colon-space-before': 'never',
    
    // SCSS特定规范
    'scss/at-rule-no-unknown': true,
    'scss/selector-no-redundant-nesting-selector': true,
    'scss/dollar-variable-pattern': '^[a-z]([a-z0-9-]+)?$',
    'scss/percent-placeholder-pattern': '^[a-z]([a-z0-9-]+)?$',
    
    // 微信小程序特定规范
    'unit-allowed-list': ['rpx', 'px', '%', 'vh', 'vw', 'em', 'rem'],
  },
  overrides: [
    {
      files: ['wechat-miniprogram/**/*.scss'],
      rules: {
        // 小程序特定规则
        'selector-class-pattern': null, // 小程序可能使用特殊命名
      },
    },
  ],
};
