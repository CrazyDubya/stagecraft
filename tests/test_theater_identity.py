from pathlib import Path
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest

SOURCE=Path(os.environ.get('THEATER_EXPORT_SOURCE',Path(__file__).resolve().parents[1]/'theater-critics/playwright_export.py'))

def normalize(text):
    return '\n'.join(line for line in text.splitlines() if not line.startswith('Generated: '))

class TheaterIdentityTests(unittest.TestCase):
    def export(self, core, specialist):
        with tempfile.TemporaryDirectory(prefix='theater-export-')as d:
            root=Path(d)
            sources={'REAL_AI_broadway_analysis.json':json.dumps(core), 'THEMATIC_resonance_analysis.json':json.dumps(specialist)}
            for name,body in sources.items():(root/name).write_text(body)
            result=subprocess.run([sys.executable,str(SOURCE)],cwd=root,text=True,capture_output=True,timeout=10)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn('Playwright export complete!',result.stdout)
            self.assertEqual({name:(root/name).read_text()for name in sources},sources)
            return {f.relative_to(root/'playwright_reports').as_posix():normalize(f.read_text())for f in(root/'playwright_reports').rglob('*.txt')}

    def fixture(self, order):
        core={'reviews':[{'musical':name,'scene_title':'Opening','scores':{'overall':score},'review_text':name+' synthetic review.'}for name,score in [('Show Alpha',9),('Show Beta',2)]]}
        specialist={'rankings':[{'musical_name':name,'scene_title':'Opening','scores':{'overall':score}}for name,score in order]}
        return core,specialist

    def check_order(self, order):
        reports=self.export(*self.fixture(order))
        alpha=reports['show_alpha/opening_analysis.txt'];beta=reports['show_beta/opening_analysis.txt']
        self.assertIn('OVERALL RATING: 9/10',alpha);self.assertIn('OVERALL RATING: 2/10',beta)
        alpha_rec=alpha.split('PLAYWRIGHT RECOMMENDATIONS',1)[1];beta_rec=beta.split('PLAYWRIGHT RECOMMENDATIONS',1)[1]
        self.assertIn('current avg: 9.0/10',alpha_rec);self.assertNotIn('current avg: 2.0/10',alpha_rec)
        self.assertIn('Focus on improving Overall (current avg: 2.0/10)',beta_rec)
        self.assertNotIn('current avg: 9.0/10',beta_rec)

    def test_alpha_first(self):
        self.check_order([('Show Alpha',9),('Show Beta',2)])

    def test_beta_first(self):
        self.check_order([('Show Beta',2),('Show Alpha',9)])

    def test_other_musical_only_does_not_supply_recommendations(self):
        core,specialist=self.fixture([('Show Alpha',9)])
        beta=self.export(core,specialist)['show_beta/opening_analysis.txt']
        recommendations=beta.split('PLAYWRIGHT RECOMMENDATIONS',1)[1]
        self.assertNotIn('current avg:',recommendations)
        self.assertIn('Consider strengthening the emotional arc',recommendations)

    def test_single_musical_all_reports_match_original_snapshot(self):
        core={'reviews':[{'musical':'Solo Show','scene_title':'Opening','scores':{'overall':9},'review_text':'Synthetic solo review.'}]}
        specialist={'rankings':[{'musical_name':'Solo Show','scene_title':'Opening','scores':{'overall':9}}]}
        expected=json.loads((Path(__file__).parent/'fixtures/theater_solo_reports.json').read_text())
        self.assertEqual(self.export(core,specialist),expected)

    def test_legacy_two_argument_helper_remains_callable(self):
        spec=importlib.util.spec_from_file_location('theater_identity_subject',SOURCE);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        _,specialist=self.fixture([('Show Alpha',9)])
        with tempfile.TemporaryDirectory()as d:
            exporter=module.PlaywrightExporter(d)
            result=exporter.generate_playwright_recommendations('Opening',{'thematic_resonance':specialist})
        self.assertTrue(any('current avg: 9.0/10'in text for text in result))

if __name__=='__main__':
    unittest.main()
