"""
BOB AI v8.0 - Machine Learning Integration

Integration layer connecting ML knowledge with prompt enhancement.
"""

from bob_ai_v8_base import BobAIV8IntegrationBase
from typing import Tuple, Dict, List, Any


class MachineLearningIntegration(BobAIV8IntegrationBase):
    """Machine learning integration for prompt enhancement."""

    def __init__(self):
        """Initialize with ML context parameters."""
        super().__init__()
        self.confidence_multipliers = {
            'machine learning': 1.4,
            'deep learning': 1.4,
            'model': 1.2,
            'training': 1.2,
            'neural network': 1.3,
            'tensorflow': 1.3,
            'pytorch': 1.3,
            'algorithm': 1.2,
            'classification': 1.2,
            'prediction': 1.1
        }

    def should_apply_to_prompt(self, prompt: str) -> Tuple[bool, float]:
        """Determine if ML knowledge should apply and confidence level."""
        prompt_lower = prompt.lower()

        # Check for ML keywords
        ml_keywords = ['machine learning', 'deep learning', 'neural network', 'model training',
                       'tensorflow', 'pytorch', 'scikit-learn', 'nlp', 'computer vision',
                       'classification', 'regression', 'clustering', 'lstm', 'transformer',
                       'feature engineering', 'hyperparameter', 'dataset', 'training data',
                       'prediction', 'inference', 'algorithm', 'deep neural']

        keyword_count = sum(1 for kw in ml_keywords if kw in prompt_lower)

        if keyword_count == 0:
            return False, 0.0

        confidence = min(0.95, 0.4 + (keyword_count * 0.1))
        return True, confidence

    def get_discipline_specific_context(self, prompt: str) -> Dict[str, Any]:
        """Extract ML-specific context from prompt."""
        prompt_lower = prompt.lower()

        context = {
            'ml_type': None,
            'use_case': None,
            'framework': None,
            'data_scale': None,
            'performance_priority': None
        }

        # Detect ML type
        if any(kw in prompt_lower for kw in ['classification', 'predict class', 'classify']):
            context['ml_type'] = 'classification'
        elif any(kw in prompt_lower for kw in ['regression', 'predict value', 'continuous']):
            context['ml_type'] = 'regression'
        elif any(kw in prompt_lower for kw in ['nlp', 'text', 'language']):
            context['ml_type'] = 'nlp'
        elif any(kw in prompt_lower for kw in ['computer vision', 'image', 'visual']):
            context['ml_type'] = 'computer_vision'
        elif any(kw in prompt_lower for kw in ['cluster', 'group', 'unsupervised']):
            context['ml_type'] = 'clustering'

        # Detect use case
        if any(kw in prompt_lower for kw in ['production', 'deploy', 'scale']):
            context['use_case'] = 'production'
        elif any(kw in prompt_lower for kw in ['research', 'experiment', 'paper']):
            context['use_case'] = 'research'
        elif any(kw in prompt_lower for kw in ['learn', 'understand', 'tutorial']):
            context['use_case'] = 'learning'

        # Detect framework
        if 'tensorflow' in prompt_lower:
            context['framework'] = 'tensorflow'
        elif 'pytorch' in prompt_lower:
            context['framework'] = 'pytorch'
        elif 'scikit-learn' in prompt_lower or 'sklearn' in prompt_lower:
            context['framework'] = 'scikit-learn'
        elif 'huggingface' in prompt_lower or 'transformers' in prompt_lower:
            context['framework'] = 'huggingface'

        # Detect data scale
        if any(kw in prompt_lower for kw in ['large scale', 'billions', 'petabyte', 'distributed']):
            context['data_scale'] = 'large'
        elif any(kw in prompt_lower for kw in ['millions', 'dataset', 'training data']):
            context['data_scale'] = 'medium'
        elif any(kw in prompt_lower for kw in ['small dataset', 'limited data', 'few samples']):
            context['data_scale'] = 'small'

        # Detect performance priority
        if any(kw in prompt_lower for kw in ['real-time', 'latency', 'edge', 'mobile']):
            context['performance_priority'] = 'latency'
        elif any(kw in prompt_lower for kw in ['accuracy', 'performance', 'metric']):
            context['performance_priority'] = 'accuracy'
        elif any(kw in prompt_lower for kw in ['interpretable', 'explainable', 'understand']):
            context['performance_priority'] = 'interpretability'

        return context

    def generate_enhancement_context(self, prompt: str, context: Dict[str, Any]) -> Dict[str, str]:
        """Generate ML-specific enhancement context."""
        enhancements = {}

        # Model selection recommendation
        ml_type = context.get('ml_type')
        if ml_type == 'classification':
            enhancements['model_guidance'] = ('Start with Logistic Regression or Random Forest baseline. '
                                            'For deep learning, use CNN for images, Transformers for text.')
        elif ml_type == 'regression':
            enhancements['model_guidance'] = ('Linear Regression for interpretability. '
                                             'Gradient Boosting (XGBoost, LightGBM) for best performance on tabular.')
        elif ml_type == 'nlp':
            enhancements['model_guidance'] = ('Use pre-trained Transformers (BERT, GPT). '
                                             'Fine-tune on task-specific data. HuggingFace library recommended.')
        elif ml_type == 'computer_vision':
            enhancements['model_guidance'] = ('Start with ResNet or Vision Transformer. '
                                             'Use transfer learning. TensorFlow/PyTorch standard.')
        elif ml_type == 'clustering':
            enhancements['model_guidance'] = ('K-Means for speed, DBSCAN for arbitrary shapes, '
                                             'Hierarchical for dendrogram visualization.')

        # Data considerations
        scale = context.get('data_scale')
        if scale == 'small':
            enhancements['data_strategy'] = ('Use data augmentation. '
                                            'Implement strong regularization. Transfer learning essential.')
        elif scale == 'large':
            enhancements['data_strategy'] = ('Implement distributed training. '
                                            'Use data pipelines (tf.data, PyTorch DataLoader). Monitor memory.')

        # Framework-specific guidance
        framework = context.get('framework')
        if framework == 'pytorch':
            enhancements['framework_tips'] = ('Dynamic graphs. Custom training loops flexible. '
                                             'Ideal for research and complex architectures.')
        elif framework == 'tensorflow':
            enhancements['framework_tips'] = ('Keras high-level API. Production deployment mature. '
                                             'TensorFlow Serving recommended for production.')
        elif framework == 'scikit-learn':
            enhancements['framework_tips'] = ('Perfect for traditional ML and tabular data. '
                                             'Minimal dependencies. Hyperparameter tuning well-documented.')

        # Priority-specific guidance
        priority = context.get('performance_priority')
        if priority == 'latency':
            enhancements['optimization'] = ('Quantization, pruning, knowledge distillation. '
                                           'TensorFlow Lite or ONNX Runtime for deployment.')
        elif priority == 'accuracy':
            enhancements['optimization'] = ('Ensemble methods, hyperparameter tuning, '
                                           'cross-validation. Regularization to prevent overfitting.')
        elif priority == 'interpretability':
            enhancements['optimization'] = ('Use tree-based models or linear models. '
                                           'Apply SHAP/LIME for black-box explanations.')

        return enhancements

    def enhance(self, prompt: str) -> str:
        """Enhance prompt with ML guidance."""
        should_apply, confidence = self.should_apply_to_prompt(prompt)

        if not should_apply or confidence < 0.3:
            return prompt

        context = self.get_discipline_specific_context(prompt)
        enhancements = self.generate_enhancement_context(prompt, context)
        recommendations = self._generate_recommendations(context)

        enhancement = f"""
{prompt}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 MACHINE LEARNING ENHANCEMENT (Confidence: {confidence:.0%})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        if enhancements.get('model_guidance'):
            enhancement += f"\n🎯 MODEL SELECTION:\n{enhancements['model_guidance']}\n"

        if enhancements.get('data_strategy'):
            enhancement += f"\n📈 DATA STRATEGY:\n{enhancements['data_strategy']}\n"

        if enhancements.get('framework_tips'):
            enhancement += f"\n⚙️ FRAMEWORK GUIDANCE:\n{enhancements['framework_tips']}\n"

        if enhancements.get('optimization'):
            enhancement += f"\n⚡ OPTIMIZATION:\n{enhancements['optimization']}\n"

        if recommendations:
            enhancement += f"\n💡 KEY RECOMMENDATIONS:\n{recommendations}\n"

        enhancement += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔑 CRITICAL ML PRINCIPLES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. START SIMPLE: Simple baseline first. Complex models rarely needed.
2. DATA QUALITY: Better data beats better models. Invest in preprocessing.
3. AVOID LEAKAGE: Don't use future information. Temporal order matters.
4. VALIDATE PROPERLY: Use K-fold CV, separate test set, stratification.
5. MONITOR DRIFT: Track performance degradation over time in production.
6. INTERPRET RESULTS: Understand WHY model makes predictions, not just WHAT.
7. ADDRESS BIAS: Check fairness, protected attributes, ethical implications.
8. DOCUMENT DECISIONS: Explain choices, limitations, future improvements.
"""
        return enhancement.strip()

    def _generate_recommendations(self, context: Dict[str, Any]) -> str:
        """Generate context-specific recommendations."""
        recommendations = []

        # ML type recommendations
        ml_type = context.get('ml_type')
        if ml_type == 'classification':
            recommendations.append('Use metrics: precision, recall, F1, AUC-ROC (not just accuracy)')
            recommendations.append('Check for class imbalance; use SMOTE or class weights if needed')
        elif ml_type == 'regression':
            recommendations.append('Use metrics: MAE, RMSE, R²')
            recommendations.append('Check residual distribution for bias')
        elif ml_type == 'nlp':
            recommendations.append('Pre-train if possible; fine-tuning more efficient than training from scratch')
            recommendations.append('Monitor for semantic drift; regular retraining needed')
        elif ml_type == 'computer_vision':
            recommendations.append('Transfer learning almost always better than training from scratch')
            recommendations.append('Data augmentation critical for small datasets')

        # Use case recommendations
        use_case = context.get('use_case')
        if use_case == 'production':
            recommendations.append('Plan monitoring: model performance, data drift, prediction latency')
            recommendations.append('Version models; maintain rollback capability')
            recommendations.append('Implement A/B testing before full deployment')
        elif use_case == 'research':
            recommendations.append('Publish reproducible results; share code and data where possible')
            recommendations.append('Conduct thorough ablation studies')

        # Data scale recommendations
        scale = context.get('data_scale')
        if scale == 'small':
            recommendations.append('Implement aggressive regularization (dropout, L1/L2)')
            recommendations.append('Cross-validation more important with limited data')
        elif scale == 'large':
            recommendations.append('Use efficient data loading (streaming, batching)')
            recommendations.append('Consider distributed training for time efficiency')

        return '\n'.join(f'• {rec}' for rec in recommendations) if recommendations else ''

    def _get_enhancement_areas(self) -> List[str]:
        """Get list of enhancement areas."""
        return [
            'Algorithm Selection',
            'Data Preprocessing',
            'Feature Engineering',
            'Model Architecture',
            'Training Strategy',
            'Evaluation Metrics',
            'Hyperparameter Tuning',
            'Production Deployment',
            'Performance Monitoring',
            'Bias and Fairness',
            'Model Interpretability',
            'Scalability Considerations'
        ]


def get_machine_learning_module() -> MachineLearningKnowledge:
    """Get ML knowledge module instance."""
    from bob_ai_v8_machine_learning import MachineLearningKnowledge
    return MachineLearningKnowledge()
