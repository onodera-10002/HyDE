import { defineConfig } from 'orval';
 
export default defineConfig({
  RAGapi: {
    input: {
        target: '../backend/openapi.json'
    },
    output: {
      target:'./src/features/api/endpoints.ts',
      schemas: './src/features/api/model',
      client: 'react-query',
      baseUrl: 'http://localhost:8005',
    },
    hooks: {
      afterAllFilesWrite: 'prettier --write',
    },
  },
  
  RAGZod: {
    input: {
      target: '../backend/openapi.json',
    },
    output: {
      target: './src/features/api/schemas', // Zodは別の場所に吐き出すのが綺麗
      client: 'zod', // ← これは「Zodのスキーマ定義を作れ」という意味。通信コードは生成されない。
      // ★ここに baseUrl は不要！
    },
  },
});