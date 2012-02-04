SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL';

CREATE SCHEMA IF NOT EXISTS `mygift` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci ;
USE `mygift` ;

-- -----------------------------------------------------
-- Table `mygift`.`user`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `mygift`.`user` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
  `email` VARCHAR(200) NOT NULL ,
  `nickname` VARCHAR(100) NULL ,
  `password` VARCHAR(100) NOT NULL ,
  `register_time` DATETIME NOT NULL ,
  `register_ip` VARCHAR(45) NULL ,
  `privilege` SMALLINT NOT NULL DEFAULT 1 COMMENT 'privilege = {0:管理员, 1:普通会员, 2:高级会员}' ,
  `status` VARCHAR(45) NOT NULL DEFAULT 'active' COMMENT '帐户状态  status = active  locked' ,
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) ,
  UNIQUE INDEX `email_UNIQUE` (`email` ASC) ,
  UNIQUE INDEX `nickname_UNIQUE` (`nickname` ASC) ,
  PRIMARY KEY (`id`) )
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci
COMMENT = '欲望清单用户表';


-- -----------------------------------------------------
-- Table `mygift`.`product`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `mygift`.`product` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
  `pkey` VARCHAR(100) NOT NULL COMMENT '商品唯一标识, 商品url的hash值' ,
  `title` VARCHAR(400) NOT NULL COMMENT '商家所卖商品标题' ,
  `url` VARCHAR(300) NOT NULL COMMENT '商品url' ,
  `image` VARCHAR(100) NULL COMMENT '商品图片,下载在服务端服务器图片' ,
  `origin_image_url` VARCHAR(300) NULL COMMENT '原始图片链接' ,
  `name` VARCHAR(300) NULL COMMENT '商品名称' ,
  `add_time` DATETIME NULL ,
  `producer` VARCHAR(100) NULL COMMENT '商品厂家' ,
  `production_place` VARCHAR(100) NULL ,
  `gross_weight` VARCHAR(100) NULL ,
  `update_time` DATETIME NOT NULL ,
  `status` VARCHAR(45) NULL DEFAULT 'on' COMMENT '商品状态 status = on, off, wait' ,
  PRIMARY KEY (`id`, `pkey`) ,
  UNIQUE INDEX `pkey_UNIQUE` (`pkey` ASC) )
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci
COMMENT = '商品表';


-- -----------------------------------------------------
-- Table `mygift`.`product_price`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `mygift`.`product_price` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
  `product_pkey` VARCHAR(100) NOT NULL COMMENT '商品id' ,
  `price` VARCHAR(100) NULL ,
  `update_time` DATETIME NOT NULL COMMENT '价格更新时间，即为抓取到变动时间' ,
  PRIMARY KEY (`id`) ,
  INDEX `product_key` (`product_pkey` ASC) ,
  INDEX `product_pkey` (`product_pkey` ASC) ,
  CONSTRAINT `product_pkey`
    FOREIGN KEY (`product_pkey` )
    REFERENCES `mygift`.`product` (`pkey` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci
COMMENT = '商品价格表';


-- -----------------------------------------------------
-- Table `mygift`.`wishlist`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `mygift`.`wishlist` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
  `user_id` INT UNSIGNED NOT NULL ,
  `product_pkey` VARCHAR(100) NOT NULL ,
  `is_shared` VARCHAR(45) NOT NULL DEFAULT 'yes' COMMENT '是否分享 is_shared = yes, no' ,
  `create_time` DATETIME NOT NULL COMMENT '愿望添加时间' ,
  `expect_price` VARCHAR(45) NULL ,
  `status` VARCHAR(45) NOT NULL DEFAULT 'follow' COMMENT '愿望状态 status = follow, deleted, ${product_price_id:表示已购买}' ,
  PRIMARY KEY (`id`, `user_id`, `product_pkey`) ,
  INDEX `member_id` (`user_id` ASC) )
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci
COMMENT = '用户欲望表';


-- -----------------------------------------------------
-- Table `mygift`.`messagebox`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `mygift`.`messagebox` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
  `user_id` INT UNSIGNED NOT NULL ,
  `message` VARCHAR(1500) NOT NULL ,
  `by` VARCHAR(45) NOT NULL DEFAULT 'system' COMMENT '消息类型 type = system, user' ,
  `status` VARCHAR(45) NOT NULL COMMENT '消息状态 status = unread, read' ,
  `start_time` DATETIME NOT NULL ,
  `end_time` DATETIME NULL ,
  PRIMARY KEY (`id`) ,
  INDEX `member_id` USING BTREE (`user_id` ASC) )
ENGINE = MyISAM
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci
COMMENT = '消息盒子';


-- -----------------------------------------------------
-- Table `mygift`.`product_comment`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `mygift`.`product_comment` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
  `product_pkey` VARCHAR(100) NOT NULL ,
  `user_id` INT UNSIGNED NOT NULL ,
  `comment` VARCHAR(900) NOT NULL ,
  `is_anonymous` VARCHAR(45) NOT NULL DEFAULT 'no' COMMENT '是否匿名 is_anonymous = no, yes' ,
  `comment_time` DATETIME NOT NULL COMMENT '评论时间' ,
  PRIMARY KEY (`id`) )
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci
COMMENT = '商品评价';



SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
