# Source Profiling Report

# customers.csv
## 1. Source Inventory
| Source | Type | Rows/Records | Key | Update Pattern | Quality Findings |
|---|---|---:|---|---|---|
| customers.csv | CSV File | 250 rows, 7 columns | customer_id(non-unique)|Full file copy (static)| 3 missing emails, 2 missing cities, 2 exact duplicates, 3 duplicate customer IDs|

## 2. Schema Findings
* **Flat-file Structure:** Contains 250 records across 7 columns (customer_id, first_name, last_name, email, city, signup_date, customer_segment).
* **Stateless Text Types:** Inferref as generic strings (str) types across all cokumns due to the laack of native schema metadata in CSV formatting.

## 3. Data Quality Findings
* **Row-Level Duplication:** Exactly 2 duplicate rows exist in the file.
* **Identifier Collisions:** The 'customer_id' column cotains duplicates (total unique count is less than 250), violating primary key uniqueness expectations.
* **Missing Attributes:** The 'email' column has 3 missing values, and the 'city' column has 2 missing values.

## 4. Recommended Acquisition Method
* Full file ingestion via pandas (pd.read_csv) paired with SHA-256 hash manifest check for change tracking.

## 5. Risks and Assumptions
* **Type Inference Limitations:** Because CSV lacks embedded typing, date fields (signup_date) will require explicit type casting during the transformation phase.

# orders.json
## 1. Source Inventory
| Source | Type | Rows/Records | Key | Update Pattern | Quality Findings |
|---|---|---:|---|---|---|
| orders.json | JSON File | 250 records, 9 columns | order_id (Candidate) | Full file copy (static) | Zero null values detected; contains nested `shipping` object |

## 2. Schema Findings
* **Top-Level Structure:** Root element is a JSON list containing 250 flat-to-semi-structured records with 9 unique top-level keys (`order_id`, `customer_id`, `order_timestamp`, `status`, `item_count`, `subtotal`, `shipping_fee`, `total_amount`, `shipping`).
* **Data Types:** Identifiers and timestamps (`order_id`, `customer_id`, `order_timestamp`, `status`) are string-typed (`str`), counts and fees use integers (`int64`), monetary amounts use floats (`float64`), and the `shipping` field is a nested dictionary (`object`).
* **Nested Fields:** The `shipping` field represents a nested object that requires flattening or a native variant/struct data type for downstream analytical processing.

## 3. Data Quality Findings
* **Completeness:** High data completeness with 0 null/missing values across all 9 top-level fields.
* **Structural Consistency:** All 250 records uniformly adhere to the 9-key top-level schema without missing keys or structural breaks.

## 4. Recommended Acquisition Method
* File copy with SHA-256 hash manifest tracking to guarantee byte-for-byte fidelity and prevent duplicate file copies during reruns.

## 5. Risks and Assumptions
* **Timestamp Parsing:** `order_timestamp` arrives as a string value and must be explicitly cast to a standardized UTC timestamp during transformation stages.
* **Nested Complexity:** Downstream reporting layers must handle the nested `shipping` object either via attribute flattening or JSON parsing.


# products.parquet
## 1. Source Inventory
| Source | Type | Rows/Records | Key | Update Pattern | Quality Findings |
|---|---|---:|---|---|---|
| products.parquet | Parquet File | 200 rows, 7 columns | product_id (Unique) | Full file copy / Static snapshot | 100% data completeness; zero nulls, zero duplicates, unique primary keys |

## 2. Schema Findings
* **Columnar Structure:** Contains 200 records across 7 strongly typed columns (`product_id`, `product_name`, `category`, `brand`, `unit_price`, `stock_quantity`, `weight_kg`).
* **Native Data Types:** Enforces strict native datatypes natively within the binary structure (`object/str` for identifiers/text, `float64` for decimals/weights, and `int32` for stock counts).

## 3. Data Quality Findings
* **Integrity:** Pristine structural integrity with zero missing values, zero exact duplicate rows, and complete uniqueness confirmed on the `product_id` column.

## 4. Recommended Acquisition Method
* Direct file read using pandas/pyarrow with a hash manifest verification to ensure secure tracking without format degradation.

## 5. Risks and Assumptions
* **Operational Unsuitability:** While highly compressed and optimized for analytics, this binary format is not suitable for transactional write-heavy source applications (OLTP).

# Local REST API

* **Volume & Structure:** Contains a total of 122 event records distributed across multiple pages. Each record contains top-level keys including 'event_id', 'customer_id', 'event_type', 'amount', 'updated_at', and a nested 'metadata' dictionary.
* **Pagination & Quality Observations:** Relies on pagination controls (page, per_page, has_more, next_page, items). Processing only page 1 captures a subset (10 records), resulting in an incomplete ingestio. The source intentionally contains duplicated event_id values with newer timestamps, requiring deterministic code-driven deduplication.

# PostgreSQL Table ('support_tickets') Profiling Summary

* **Table Structure:** Contains 8 columns (ticket_id, customer_id, category, priority, assigned_agent, opened_at, resolved_at, and status) backed by a primary key on ticket_id.
* **Data Types & Constraints:** Utilizes strongly-typed relational fields: 'integer' for IDs , character varying for text attributes, and timestamp without time zone for dates. Nullability is enforced on primary keys and core categorizations, while 'assigned_agent' and 'resolved_at' allow nullable states.
* **Record Volume & Completeness:** Total row count is exactly 250 records. Inspection confirms 4 record contain unassigned agents.