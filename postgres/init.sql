-- Initialize PartSelect database

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create products table is handled by SQLAlchemy, but we can add indexes here
CREATE INDEX IF NOT EXISTS idx_products_part_number ON products(part_number);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_appliance_type ON products(appliance_type);

-- Create compatibility indexes
CREATE INDEX IF NOT EXISTS idx_compatibility_model_number ON compatibility(model_number);
CREATE INDEX IF NOT EXISTS idx_compatibility_product_id ON compatibility(product_id);

-- Create conversations indexes
CREATE INDEX IF NOT EXISTS idx_conversations_conversation_id ON conversations(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);