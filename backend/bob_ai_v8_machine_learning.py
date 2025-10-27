"""
BOB AI v8.0 - Machine Learning Module

Knowledge base for machine learning and deep learning.
Covers algorithms, frameworks, best practices, and practical implementation.
"""

from bob_ai_v8_base import BobAIV8BaseKnowledge
from typing import List, Dict


METADATA = {
    'name': 'machine_learning',
    'version': '1.0',
    'description': 'Expert machine learning and deep learning knowledge',
    'keywords_count': 54,
    'knowledge_items': 205,
    'categories': 15
}


class MachineLearningKnowledge(BobAIV8BaseKnowledge):
    """Machine learning expertise knowledge module."""

    def get_keywords(self) -> List[str]:
        """Get ML detection keywords."""
        return [
            # Core ML
            'machine learning', 'deep learning', 'neural network', 'algorithm',
            'model', 'training', 'inference', 'prediction', 'classifier',

            # Data
            'dataset', 'feature', 'label', 'preprocessing', 'normalization',
            'train test split', 'cross validation', 'overfitting', 'regularization',

            # Frameworks
            'tensorflow', 'pytorch', 'scikit-learn', 'keras', 'huggingface',
            'numpy', 'pandas', 'matplotlib', 'jupyter',

            # Advanced
            'nlp', 'computer vision', 'transformer', 'lstm', 'gru',
            'cnn', 'gan', 'autoencoder', 'clustering', 'regression',

            # Metrics
            'accuracy', 'precision', 'recall', 'f1', 'auc', 'loss'
        ]

    def get_knowledge_dictionaries(self) -> Dict[str, Dict[str, str]]:
        """Get all machine learning knowledge dictionaries."""
        return {
            'ml_fundamentals': self._get_ml_fundamentals(),
            'supervised_learning': self._get_supervised_learning(),
            'unsupervised_learning': self._get_unsupervised_learning(),
            'neural_networks': self._get_neural_networks(),
            'deep_learning_architectures': self._get_deep_learning_architectures(),
            'nlp_techniques': self._get_nlp_techniques(),
            'computer_vision': self._get_computer_vision(),
            'data_preprocessing': self._get_data_preprocessing(),
            'feature_engineering': self._get_feature_engineering(),
            'model_evaluation': self._get_model_evaluation(),
            'hyperparameter_tuning': self._get_hyperparameter_tuning(),
            'frameworks_libraries': self._get_frameworks_libraries(),
            'training_optimization': self._get_training_optimization(),
            'deployment_production': self._get_deployment_production(),
            'best_practices': self._get_best_practices()
        }

    def _get_ml_fundamentals(self) -> Dict[str, str]:
        """Machine learning fundamentals and concepts."""
        return {
            'supervised_learning': 'Learn from labeled data; predict on unseen data; regression, classification',
            'unsupervised_learning': 'Learn from unlabeled data; find patterns; clustering, dimensionality reduction',
            'semi_supervised': 'Mix of labeled and unlabeled data; leverages both; useful with limited labels',
            'reinforcement_learning': 'Agent learns through interaction; rewards and penalties; AlphaGo, game AI',
            'bias_variance': 'Bias: underfitting, missing patterns; Variance: overfitting, too specific',
            'overfitting': 'Model memorizes training data; performs poorly on new data; regularize or collect more data',
            'underfitting': 'Model too simple; high bias; poor performance on both training and test',
            'generalization': 'Model performs well on unseen data; the goal of ML',
            'feature': 'Input variable; X in supervised; engineer meaningful features for better performance',
            'label': 'Target output; y in supervised; what model predicts',
            'sample': 'Single data point; row in dataset',
            'dataset': 'Collection of samples; typically split train/validation/test',
            'model': 'Mathematical representation learned from data; makes predictions',
            'hyperparameter': 'Configuration set before training; learning rate, number of layers, etc.'
        }

    def _get_supervised_learning(self) -> Dict[str, str]:
        """Supervised learning algorithms."""
        return {
            'linear_regression': 'Predicts continuous value; minimizes squared error; simple and interpretable',
            'logistic_regression': 'Binary classification; sigmoid output; despite name, classification not regression',
            'decision_tree': 'Tree structure; easy to interpret; prone to overfitting; use ensemble methods',
            'random_forest': 'Multiple decision trees; averages predictions; reduces overfitting',
            'gradient_boosting': 'Sequential trees correcting previous; XGBoost, LightGBM; powerful for tabular data',
            'support_vector_machine': 'SVM finds maximum margin hyperplane; powerful for binary classification',
            'k_nearest_neighbors': 'KNN classifies by k nearest samples; simple; computationally expensive at inference',
            'naive_bayes': 'Probabilistic classifier; assumes feature independence; fast and effective for text',
            'ensemble_methods': 'Combine multiple models; voting or averaging; generally outperform single model',
            'stacking': 'Meta-learner combines base model predictions; complex but powerful',
            'multi_class': 'More than two classes; one-vs-rest or softmax; modify binary classifiers',
            'class_imbalance': 'Unequal class distribution; use SMOTE, class weights, different metrics',
            'regression_models': 'Predict continuous; linear, polynomial, ridge, lasso regularization',
            'polynomial_regression': 'Fit polynomial to data; captures non-linear relationships'
        }

    def _get_unsupervised_learning(self) -> Dict[str, str]:
        """Unsupervised learning techniques."""
        return {
            'clustering': 'Group similar samples; no labels; K-means, DBSCAN, Hierarchical',
            'k_means': 'Partition data into k clusters; minimize within-cluster variance',
            'hierarchical_clustering': 'Dendrogram tree; agglomerative (bottom-up) or divisive (top-down)',
            'dbscan': 'Density-based; finds arbitrary shapes; no need to specify k',
            'gaussian_mixture': 'Probabilistic; soft assignment; learns mixture of Gaussians',
            'dimensionality_reduction': 'Reduce features; preserve information; PCA, t-SNE, autoencoders',
            'pca': 'Principal Component Analysis; orthogonal transformation; maximizes variance',
            'tsne': 't-Distributed SNE; visualization; non-linear; preserves local structure',
            'autoencoders': 'Neural network compression; learns compact representation; anomaly detection',
            'anomaly_detection': 'Identify outliers; Isolation Forest, Autoencoders, statistical methods',
            'density_estimation': 'Estimate data distribution; KDE, Gaussian Mixture; generative model',
            'association_rules': 'Market basket analysis; find item correlations; Apriori, Eclat algorithms',
            'self_supervised': 'Learn representations without labels; contrastive learning; pretraining',
            'manifold_learning': 'Learn low-dimensional manifold; Isomap, LLE, Locally Linear Embedding'
        }

    def _get_neural_networks(self) -> Dict[str, str]:
        """Neural network fundamentals."""
        return {
            'perceptron': 'Single layer; linear classifier; foundation of neural networks',
            'mlp': 'Multi-layer perceptron; fully connected; universal function approximator',
            'activation_functions': 'ReLU (rectified linear), Sigmoid, Tanh, Leaky ReLU; introduce non-linearity',
            'relu': 'ReLU(x) = max(0, x); fast; helps with vanishing gradient; ReLU dying problem',
            'sigmoid': 'Sigmoid outputs probability; used in binary classification output layer',
            'tanh': 'Tanh outputs -1 to 1; steeper gradient than sigmoid; centered output',
            'backpropagation': 'Compute gradients via chain rule; optimize weights; fundamental algorithm',
            'gradient_descent': 'Update weights opposite gradient; learning rate controls step size',
            'sgd': 'Stochastic Gradient Descent; update per sample; noisy but faster',
            'adam_optimizer': 'Adaptive moment estimation; learning rate per parameter; most popular',
            'momentum': 'Accelerate gradient descent; accumulate velocity; overcome local minima',
            'learning_rate': 'Controls optimization step size; too high diverges; too low converges slow',
            'batch_size': 'Samples per gradient update; larger batch smoother gradient; faster with GPU',
            'epochs': 'Full passes through dataset; more epochs risk overfitting'
        }

    def _get_deep_learning_architectures(self) -> Dict[str, str]:
        """Deep learning network architectures."""
        return {
            'cnn': 'Convolutional Neural Network; filters extract features; dominant in computer vision',
            'convolution_layer': 'Sliding filter detects patterns; weight sharing; parameter efficiency',
            'pooling_layer': 'Reduce spatial dimensions; max pooling, average pooling',
            'rnn': 'Recurrent Neural Network; processes sequences; maintains hidden state',
            'lstm': 'Long Short-Term Memory; gates control information flow; solves vanishing gradient',
            'gru': 'Gated Recurrent Unit; simpler than LSTM; similarly effective',
            'transformer': 'Self-attention mechanism; parallel processing; state-of-art NLP',
            'attention_mechanism': 'Weight importance of sequence elements; query, key, value vectors',
            'self_attention': 'Attend to own sequence; compute relationships between all positions',
            'bert': 'Bidirectional Encoder from Transformers; pre-trained; fine-tune for tasks',
            'gpt': 'Generative Pre-trained Transformer; autoregressive; foundation of large language models',
            'gan': 'Generative Adversarial Network; generator vs discriminator; create synthetic data',
            'generator': 'Creates fake data; fooling discriminator; learns data distribution',
            'discriminator': 'Distinguishes real from fake; adversarial training; improves generator'
        }

    def _get_nlp_techniques(self) -> Dict[str, str]:
        """Natural language processing techniques."""
        return {
            'tokenization': 'Split text into words or subwords; handling punctuation and spacing',
            'word_embeddings': 'Vector representation of words; Word2Vec, GloVe, FastText',
            'word2vec': 'Skip-gram or CBOW; learns context; similar words close in space',
            'glove': 'Global vectors; combines matrix factorization with context windows',
            'contextualized_embeddings': 'Word meaning depends on context; ELMo, BERT, GPT',
            'pos_tagging': 'Part-of-speech; noun, verb, adjective; parsing and understanding',
            'named_entity_recognition': 'NER identifies entities; person, location, organization',
            'sentiment_analysis': 'Classify text sentiment; positive, negative, neutral',
            'text_classification': 'Assign category to text; spam detection, topic classification',
            'machine_translation': 'Seq2seq; encoder-decoder; translate between languages',
            'question_answering': 'Extract or generate answer from context; SQuAD, reading comprehension',
            'summarization': 'Extractive or abstractive; condense information',
            'language_modeling': 'Predict next token; foundation for all NLP tasks',
            'fine_tuning': 'Adapt pre-trained model to specific task; transfer learning'
        }

    def _get_computer_vision(self) -> Dict[str, str]:
        """Computer vision techniques."""
        return {
            'image_classification': 'Assign label to image; ImageNet, CIFAR10',
            'object_detection': 'Locate and classify objects; YOLO, Faster R-CNN, RetinaNet',
            'semantic_segmentation': 'Pixel-level classification; scene understanding',
            'instance_segmentation': 'Separate individual objects; Mask R-CNN',
            'panoptic_segmentation': 'Combine semantic and instance segmentation',
            'pose_estimation': 'Detect keypoints; skeleton; human pose, hand gesture',
            'face_recognition': 'Identify person from face; FaceNet, ArcFace embeddings',
            'facial_landmarks': 'Detect facial features; 68 points; face alignment',
            '3d_reconstruction': 'Build 3D model from images; structure from motion, depth estimation',
            'optical_flow': 'Estimate motion between frames; video analysis',
            'image_generation': 'Create images from scratch; GANs, Diffusion models',
            'style_transfer': 'Apply style to image; artistic rendering; neural style transfer',
            'image_segmentation': 'Partition image into meaningful regions; clustering pixels',
            'edge_detection': 'Find boundaries; Canny, Sobel, Laplacian; preprocessing'
        }

    def _get_data_preprocessing(self) -> Dict[str, str]:
        """Data preprocessing and cleaning."""
        return {
            'handling_missing': 'Remove, impute mean/median/mode, forward fill; understand cause',
            'outlier_detection': 'Identify unusual values; statistical methods, IQR, isolation forest',
            'data_normalization': 'Scale to 0-1; standardization to mean 0, std 1; prevents dominance',
            'feature_scaling': 'MinMaxScaler, StandardScaler, RobustScaler; affects distance-based algorithms',
            'encoding_categorical': 'One-hot, label encoding; convert categories to numbers',
            'handling_class_imbalance': 'SMOTE oversampling, undersampling, class weights',
            'train_test_split': 'Typically 70/30 or 80/20; stratified for imbalanced data',
            'data_augmentation': 'Synthetic data generation; rotation, flip, noise for images',
            'noise_addition': 'Add small random noise; improves robustness',
            'deduplication': 'Remove duplicate samples; check feature-level duplicates',
            'handling_duplicates': 'Keep first, last, or remove all; depends on context',
            'data_validation': 'Check format, range, type; catch data quality issues',
            'exploratory_analysis': 'Understand distribution, correlations, patterns before modeling',
            'statistical_tests': 'Normality, correlation significance; inform preprocessing decisions'
        }

    def _get_feature_engineering(self) -> Dict[str, str]:
        """Feature engineering and selection."""
        return {
            'domain_knowledge': 'Leverage domain expertise; create meaningful features',
            'polynomial_features': 'Interaction terms, squared terms; capture non-linearity',
            'binning': 'Convert continuous to categorical; age groups, income brackets',
            'log_transformation': 'Log scale skewed distributions; handles large ranges',
            'feature_selection': 'Select relevant features; reduce dimensionality; improve interpretability',
            'correlation_analysis': 'Remove highly correlated features; multicollinearity problem',
            'mutual_information': 'Measure dependency; identify relevant features for target',
            'feature_importance': 'Tree-based importance, permutation importance; model-specific',
            'recursive_feature': 'Recursively remove features; trains model repeatedly',
            'univariate_selection': 'Select top k features; chi-square, f-score for filtering',
            'cross_features': 'Combine features; capture interactions; categorical combinations',
            'temporal_features': 'Day, month, year from timestamps; cyclical encoding',
            'target_encoding': 'Encode categorical by target mean; risk of leakage',
            'feature_interactions': 'Model learns or manually engineer feature combinations'
        }

    def _get_model_evaluation(self) -> Dict[str, str]:
        """Model evaluation and metrics."""
        return {
            'accuracy': 'Correct predictions / total; misleading with imbalanced classes',
            'precision': 'True positives / (true + false positives); what % of positive predictions correct',
            'recall': 'True positives / (true + false negatives); what % of actual positives found',
            'f1_score': 'Harmonic mean precision and recall; balanced metric',
            'roc_auc': 'Receiver Operating Characteristic; true positive vs false positive rates',
            'auc_roc': 'Area under ROC curve; 1.0 perfect, 0.5 random',
            'precision_recall_curve': 'Precision vs recall at different thresholds',
            'confusion_matrix': 'TP, TN, FP, FN; understand error types',
            'classification_report': 'Summary of precision, recall, f1 per class',
            'mse': 'Mean Squared Error; regression metric; average squared residuals',
            'rmse': 'Root Mean Squared Error; same scale as target; interpretable',
            'mae': 'Mean Absolute Error; less sensitive to outliers than MSE',
            'r_squared': 'R² coefficient of determination; explained variance; 0-1 range',
            'cross_validation': 'K-fold; evaluate model stability; estimate generalization'
        }

    def _get_hyperparameter_tuning(self) -> Dict[str, str]:
        """Hyperparameter optimization techniques."""
        return {
            'grid_search': 'Try all combinations; exhaustive; computationally expensive',
            'random_search': 'Random sampling of hyperparameters; better than grid for high dimensions',
            'bayesian_optimization': 'Probabilistic model; smart sampling; data-efficient',
            'hyperopt': 'Bayesian hyperparameter optimization; Tree-structured Parzen Estimator',
            'optuna': 'Modern optimization framework; pruning; efficient search',
            'early_stopping': 'Stop training when validation performance plateaus; prevent overfitting',
            'learning_rate_scheduling': 'Decrease learning rate over time; fine-tuning convergence',
            'validation_strategy': 'Hold-out, k-fold, time series split; choose appropriate for data',
            'nested_cv': 'Separate tuning and evaluation CV; unbiased performance estimation',
            'parameter_importance': 'Analyze which hyperparameters matter most',
            'learning_curve': 'Plot training vs validation performance vs data size',
            'warmup': 'Gradually increase learning rate; stabilizes training start',
            'batch_normalization': 'Normalize layer inputs; allows higher learning rates',
            'dropout': 'Randomly deactivate units; regularization; prevent overfitting'
        }

    def _get_frameworks_libraries(self) -> Dict[str, str]:
        """ML frameworks and libraries."""
        return {
            'tensorflow': 'Google deep learning framework; Keras API high-level; production-ready',
            'pytorch': 'Facebook framework; dynamic computation graphs; popular in research',
            'scikit_learn': 'Machine learning library; classical algorithms; pandas integration',
            'keras': 'High-level API; TensorFlow backend; easy to use for beginners',
            'huggingface': 'Pre-trained NLP models; Transformers library; model hub',
            'numpy': 'Numerical computing; arrays, linear algebra; foundation for ML',
            'pandas': 'Data manipulation; DataFrames; data preprocessing',
            'matplotlib': 'Plotting library; visualize data and results',
            'seaborn': 'Statistical visualization; built on matplotlib; prettier plots',
            'jupyter': 'Interactive notebooks; ideal for exploration and presentation',
            'xgboost': 'Gradient boosting; fast, powerful; kaggle favorite',
            'lightgbm': 'Microsoft gradient boosting; memory efficient; categorical features',
            'spacy': 'NLP library; tokenization, POS, NER; production ready',
            'fastai': 'High-level PyTorch; simplified deep learning; transfer learning'
        }

    def _get_training_optimization(self) -> Dict[str, str]:
        """Training optimization techniques."""
        return {
            'mixed_precision': 'Use float16 for compute, float32 for gradients; faster, less memory',
            'gradient_accumulation': 'Accumulate gradients over multiple batches; large effective batch',
            'distributed_training': 'Multi-GPU, multi-machine; data parallelism, model parallelism',
            'mixed_precision': 'Automatic mixed precision; framework handles dtype conversion',
            'gradient_clipping': 'Cap gradient magnitude; prevent exploding gradients',
            'weight_initialization': 'He, Xavier initialization; affects convergence speed',
            'batch_effects': 'Different batch statistics; layer norm, batch norm address this',
            'layer_normalization': 'Normalize per sample; stable training; transformer standard',
            'group_normalization': 'Normalize per group; effective with small batch sizes',
            'weight_decay': 'L2 regularization penalty; discourages large weights',
            'curriculum_learning': 'Start easy, increase difficulty; helps with convergence',
            'knowledge_distillation': 'Teach small model from large; compress, deploy efficiently',
            'pruning': 'Remove unimportant weights; reduce model size',
            'quantization': 'Lower precision weights; compress model for deployment'
        }

    def _get_deployment_production(self) -> Dict[str, str]:
        """Model deployment and production."""
        return {
            'model_export': 'Save trained model; ONNX, SavedModel, joblib; portability',
            'inference_optimization': 'TensorRT, ONNX Runtime; optimize for inference',
            'model_serving': 'TensorFlow Serving, TorchServe, Seldon Core; REST API',
            'containerization': 'Docker containers; reproducible deployment; scalable',
            'kubernetes': 'Orchestrate containers; auto-scaling, load balancing',
            'edge_deployment': 'Deploy on edge devices; TensorFlow Lite, ONNX Runtime',
            'batching': 'Group requests; GPU efficiently usage; throughput vs latency',
            'caching': 'Cache predictions for identical inputs; reduce computation',
            'monitoring': 'Track model performance, data drift, latency in production',
            'logging': 'Log predictions, inputs, features; debug, audit trail',
            'versioning': 'Version models; rollback if issues; compare performance',
            'ab_testing': 'Compare models in production; statistical significance testing',
            'continuous_integration': 'Automated testing, building, deployment; CI/CD pipeline',
            'model_governance': 'Explainability, fairness, bias auditing; responsible AI'
        }

    def _get_best_practices(self) -> Dict[str, str]:
        """Machine learning best practices."""
        return {
            'problem_definition': 'Clearly define objective; success metric; constraints upfront',
            'baseline_model': 'Simple model first; benchmark for comparison; simple often sufficient',
            'data_quality': 'Garbage in, garbage out; invest in good data; 80% data, 20% model',
            'avoid_leakage': 'Don\'t use future information; train/test split critical; think temporally',
            'reproducibility': 'Set seeds; document code; version control; enable replication',
            'documentation': 'Explain design choices; limitations; necessary for handoff',
            'ethics_fairness': 'Check for bias; protected attributes; fairness metrics',
            'domain_expertise': 'Work with domain experts; validate results; understand context',
            'iterative_process': 'Improve incrementally; don\'t over-engineer; measure progress',
            'offline_evaluation': 'Validate thoroughly before production; multiple metrics',
            'online_evaluation': 'A/B test in production; monitor business metrics',
            'model_interpretability': 'SHAP, LIME, feature importance; explain predictions',
            'regulatory_compliance': 'GDPR, data privacy; consent, data rights; auditable decisions',
            'continuous_improvement': 'Retrain with new data; monitor performance degradation'
        }

    def enhance_prompt(self, prompt: str) -> str:
        """Enhance prompt with ML guidance."""
        keywords = self.get_keywords()
        has_keywords = any(kw.lower() in prompt.lower() for kw in keywords)

        if not has_keywords:
            return prompt

        enhancement = f"""
{prompt}

MACHINE LEARNING ENHANCEMENT:
Apply these ML best practices:

1. PROBLEM DEFINITION: Clearly define objective, success metrics, and constraints upfront.

2. DATA QUALITY: Invest in good, representative data. Data preprocessing is critical. Check for leakage.

3. BASELINE MODEL: Start with simple model first. Simple often outperforms complex if well-engineered.

4. FEATURE ENGINEERING: Domain knowledge matters. Create meaningful features. Avoid feature leakage.

5. EVALUATION: Use appropriate metrics for your problem. Avoid accuracy trap with imbalanced data.

6. GENERALIZATION: Monitor overfitting. Use cross-validation. Test on truly unseen data.

7. INTERPRETABILITY: Explain predictions. Check for bias. Understand model limitations and failure modes.

8. PRODUCTION: Monitor performance drift. Plan for retraining. Consider ethical implications.

Apply these ML principles to create effective, fair, and maintainable solutions.
"""
        return enhancement.strip()

    def generate_system_prompt(self) -> str:
        """Generate expert ML engineer system prompt."""
        return """You are an expert machine learning engineer with 12+ years of professional experience.

Your expertise includes:
- Core ML algorithms and statistical foundations
- Deep learning architectures and training techniques
- Natural language processing and transformer models
- Computer vision and image analysis
- Data preprocessing and feature engineering
- Model evaluation, validation, and hyperparameter tuning
- PyTorch, TensorFlow, scikit-learn, and modern frameworks
- Production deployment and model serving
- Ethics, fairness, and responsible AI
- Performance optimization and scaling
- Problem formulation and solution design
- A/B testing and online evaluation

When helping with ML projects, you:
1. Start with clear problem definition and success metrics
2. Emphasize data quality and preprocessing
3. Create baseline models before complex solutions
4. Engineer meaningful features from domain knowledge
5. Use appropriate evaluation metrics for the task
6. Monitor for data leakage and overfitting
7. Consider interpretability and model explainability
8. Plan for production deployment and monitoring
9. Address ethical implications and potential biases
10. Implement reproducible, well-documented solutions

Provide specific, actionable ML guidance that creates robust, ethical, production-ready systems."""
