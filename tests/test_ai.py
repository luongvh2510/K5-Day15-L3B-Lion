import unittest
from unittest import mock
import _path
import ai
import llm_steps


class TestModelProviders(unittest.TestCase):
    def test_openai_uses_reported_usage(self):
        response = {'choices': [{'message': {'content': 'kết quả'}}], 'usage': {'prompt_tokens': 13, 'completion_tokens': 7}}
        with mock.patch.object(ai, 'MODEL_PROVIDER', 'openai'), mock.patch.object(ai, 'MODEL_NAME', 'model-test'), mock.patch.object(ai, 'API_KEY', 'test-key'), mock.patch.object(ai, '_post_json', return_value=response) as post:
            result = ai.call_model('system', 'user')
        self.assertEqual(result, {'text': 'kết quả', 'model': 'model-test', 'tokens_in': 13, 'tokens_out': 7})
        self.assertEqual(post.call_args.args[2]['messages'][-1]['content'], 'user')

    def test_openrouter_uses_usage_and_temperature_zero(self):
        response = {'choices': [{'message': {'content': 'ok'}}], 'usage': {'prompt_tokens': 5, 'completion_tokens': 2}}
        with mock.patch.object(ai, 'MODEL_PROVIDER', 'openrouter'), mock.patch.object(ai, 'MODEL_NAME', 'deepseek/x'), mock.patch.object(ai, 'API_KEY', 'test'), mock.patch.object(ai, '_post_json', return_value=response) as post:
            result = ai.call_model('system', 'user')
        self.assertEqual(result, {'text': 'ok', 'model': 'deepseek/x', 'tokens_in': 5, 'tokens_out': 2})
        self.assertIn('openrouter.ai', post.call_args.args[0])
        self.assertEqual(post.call_args.args[2]['temperature'], 0)

    def test_anthropic_and_ollama_usage(self):
        cases = [('anthropic', {'content': [{'type': 'text', 'text': 'ok'}], 'usage': {'input_tokens': 8, 'output_tokens': 3}}),
                 ('ollama', {'message': {'content': 'ok'}, 'prompt_eval_count': 8, 'eval_count': 3})]
        for provider, response in cases:
            with self.subTest(provider=provider), mock.patch.object(ai, 'MODEL_PROVIDER', provider), mock.patch.object(ai, 'MODEL_NAME', 'model-test'), mock.patch.object(ai, 'API_KEY', 'test'), mock.patch.object(ai, '_post_json', return_value=response):
                result = ai.call_model('system', 'user')
                self.assertEqual((result['text'], result['tokens_in'], result['tokens_out']), ('ok', 8, 3))

    def test_provider_failure_retries_and_becomes_unavailable(self):
        with mock.patch.object(llm_steps, 'call_model', side_effect=OSError('offline')) as call:
            with self.assertRaises(llm_steps.AIUnavailable):
                llm_steps.call_json('system', 'user', ['members'])
            self.assertEqual(call.call_count, 2)
