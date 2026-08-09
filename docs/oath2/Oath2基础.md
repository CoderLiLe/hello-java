# OAuth2 基础

## 1. OAuth2 概述

OAuth2 是一个开放标准的授权协议，允许用户授权第三方应用访问其存储在资源服务器上的信息，而不需要将用户名和密码提供给第三方应用。

### 1.1 核心角色
- **Resource Owner**：资源拥有者（用户）
- **Client**：第三方应用
- **Authorization Server**：授权服务器
- **Resource Server**：资源服务器

### 1.2 四种授权模式
- **授权码模式（Authorization Code）**：最安全，用于服务端应用（推荐）
- **隐式模式（Implicit）**：用于浏览器端应用（已不推荐）
- **密码模式（Password）**：用户直接把密码给客户端（已不推荐）
- **客户端凭证模式（Client Credentials）**：用于服务间通信

## 2. JWT 令牌

- **Header**：签名算法 + 令牌类型
- **Payload**：声明（claims）+ 过期时间
- **Signature**：对 Header + Payload 的签名

## 3. Spring Security OAuth2

Spring Security 提供对 OAuth2 的完整支持，包括授权服务器、资源服务器和客户端。
