// Real filesystem and real multipart upload (no fs mock): the download must survive any evidence title.
import { describe, it, expect } from 'vitest';
import express from 'express';
import request from 'supertest';
import os from 'os';
import path from 'path';
import { mkdtempSync } from 'fs';

async function makeApp() {
  process.env.UPLOAD_PATH = mkdtempSync(path.join(os.tmpdir(), 'evidence-'));
  const { default: createEvidenceRoutes } = await import('../evidence.js');
  const app = express();
  app.use(express.json());
  app.use('/api/evidence', createEvidenceRoutes());
  return app;
}

async function upload(app: express.Application, title: string) {
  const res = await request(app)
    .post('/api/evidence')
    .field('title', title)
    .field('type', 'document')
    .field('description', 'd')
    .field('submittedBy', 'a')
    .field('caseId', 'c')
    .attach('files', Buffer.from('hello'), { filename: 'a.txt', contentType: 'text/plain' });
  const id = res.body?.evidence?.[0]?.id ?? res.body?.evidence?.id ?? res.body?.id;
  expect(id).toBeTruthy();
  return id as string;
}

describe('GET /api/evidence/:id/file filename handling', () => {
  it.each(['Contract', 'Contract “signed” copy', 'Receipt — Q3', 'Bill 😀'])(
    'serves the file for title %s',
    async (title) => {
      const app = await makeApp();
      const id = await upload(app, title);
      const res = await request(app).get(`/api/evidence/${id}/file`);
      expect(res.status).toBe(200);
      expect(res.headers['content-disposition']).toMatch(/^attachment/);
    }
  );

  it('does not let a title inject extra Content-Disposition parameters', async () => {
    const app = await makeApp();
    const id = await upload(app, `He said "hi"; filename*=UTF-8''x.exe`);
    const res = await request(app).get(`/api/evidence/${id}/file`);
    expect(res.status).toBe(200);
    // one quoted filename parameter only: every inner quote must be escaped
    expect(res.headers['content-disposition']).toMatch(/^attachment; filename="(?:[^"\\]|\\.)*"$/);
  });
});
