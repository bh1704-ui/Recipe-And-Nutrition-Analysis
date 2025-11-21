DROP DATABASE IF EXISTS NutritionDB;
CREATE DATABASE NutritionDB;
USE NutritionDB;

-- =========================================================
-- DROP TABLES IN CORRECT ORDER
-- =========================================================
DROP TABLE IF EXISTS MealPlan_Recipes;
DROP TABLE IF EXISTS MealPlan_Recipe;
DROP TABLE IF EXISTS Feedback;
DROP TABLE IF EXISTS User_Diet_Log;
DROP TABLE IF EXISTS Recipe_Ingredient;
DROP TABLE IF EXISTS Nutrition;
DROP TABLE IF EXISTS Ingredient;
DROP TABLE IF EXISTS Recipe;
DROP TABLE IF EXISTS Meal_Plan;
DROP TABLE IF EXISTS User_Weight_History;
DROP TABLE IF EXISTS Recipe_Log;
DROP TABLE IF EXISTS User;

-- =========================================================
-- USER TABLE
-- =========================================================
CREATE TABLE User (
  User_ID INT AUTO_INCREMENT PRIMARY KEY,
  Name VARCHAR(100) NOT NULL,
  Email VARCHAR(255) NOT NULL UNIQUE,
  Password VARCHAR(255) NOT NULL,
  Gender ENUM('Male','Female','Other') DEFAULT 'Other',
  Date_Of_Birth DATE,
  Height_cm SMALLINT UNSIGNED CHECK (Height_cm > 0),
  Weight_kg DECIMAL(5,2) CHECK (Weight_kg > 0),
  Activity_Level ENUM('Sedentary','Light','Moderate','Active','Very Active') DEFAULT 'Moderate',
  Dietary_Preferences VARCHAR(100),
  Allergies VARCHAR(255),
  BMI DECIMAL(5,2) DEFAULT NULL,
  role ENUM('user','admin') NOT NULL DEFAULT 'user',
  Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  Updated_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- =========================================================
-- RECIPE TABLE
-- =========================================================
CREATE TABLE Recipe (
  Recipe_ID INT AUTO_INCREMENT PRIMARY KEY,
  Recipe_Name VARCHAR(200) NOT NULL,
  Description TEXT,
  Cuisine_Type VARCHAR(100),
  Preparation_Time_minutes SMALLINT UNSIGNED DEFAULT 0,
  Cooking_Time_minutes SMALLINT UNSIGNED DEFAULT 0,
  Serving_Size DECIMAL(4,2) NOT NULL DEFAULT 1,
  Difficulty_Level ENUM('Easy','Medium','Hard') DEFAULT 'Easy',
  Instructions TEXT,
  Creator_User_ID INT,
  Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  Updated_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_recipe_creator
    FOREIGN KEY (Creator_User_ID) REFERENCES User(User_ID)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- =========================================================
-- INGREDIENT TABLE
-- =========================================================
CREATE TABLE Ingredient (
  Ingredient_ID INT AUTO_INCREMENT PRIMARY KEY,
  Ingredient_Name VARCHAR(150) NOT NULL UNIQUE,
  Unit_Of_Measure VARCHAR(50) NOT NULL,
  Category VARCHAR(50) NOT NULL,
  Notes VARCHAR(255),
  Updated_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- =========================================================
-- NUTRITION TABLE
-- =========================================================
CREATE TABLE Nutrition (
  Nutrition_ID INT AUTO_INCREMENT PRIMARY KEY,
  Ingredient_ID INT NOT NULL UNIQUE,
  Calories DECIMAL(6,2) DEFAULT 0,
  Carbohydrates_g DECIMAL(6,2) DEFAULT 0,
  Protein_g DECIMAL(6,2) DEFAULT 0,
  Fat_g DECIMAL(6,2) DEFAULT 0,
  Fiber_g DECIMAL(6,2) DEFAULT 0,
  Vitamins VARCHAR(255),
  Minerals VARCHAR(255),
  Other_Nutrients TEXT,
  Updated_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_nutrition_ingredient
    FOREIGN KEY (Ingredient_ID) REFERENCES Ingredient(Ingredient_ID)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- =========================================================
-- RECIPE INGREDIENT TABLE
-- =========================================================
CREATE TABLE Recipe_Ingredient (
  RecipeIngredient_ID INT AUTO_INCREMENT PRIMARY KEY,
  Recipe_ID INT NOT NULL,
  Ingredient_ID INT NOT NULL,
  Quantity DECIMAL(8,3) NOT NULL CHECK (Quantity > 0),
  Unit VARCHAR(50) NOT NULL,

  CONSTRAINT fk_ri_recipe
    FOREIGN KEY (Recipe_ID)
    REFERENCES Recipe(Recipe_ID)
    ON DELETE CASCADE ON UPDATE CASCADE,

  CONSTRAINT fk_ri_ingredient
    FOREIGN KEY (Ingredient_ID)
    REFERENCES Ingredient(Ingredient_ID)
    ON DELETE RESTRICT ON UPDATE CASCADE,

  UNIQUE (Recipe_ID, Ingredient_ID)
) ENGINE=InnoDB;

-- =========================================================
-- USER DIET LOG
-- =========================================================
CREATE TABLE User_Diet_Log (
  Log_ID INT AUTO_INCREMENT PRIMARY KEY,
  User_ID INT,
  Recipe_ID INT,
  Date DATE NOT NULL,
  Time TIME,
  Portion_Size DECIMAL(5,2) DEFAULT 1,
  Notes TEXT,
  is_finished BOOLEAN DEFAULT FALSE,
  Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  Updated_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  FOREIGN KEY (User_ID) REFERENCES User(User_ID)
    ON DELETE CASCADE ON UPDATE CASCADE,

  FOREIGN KEY (Recipe_ID) REFERENCES Recipe(Recipe_ID)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- =========================================================
-- MEAL PLAN
-- =========================================================
CREATE TABLE Meal_Plan (
  MealPlan_ID INT AUTO_INCREMENT PRIMARY KEY,
  User_ID INT,
  Plan_Name VARCHAR(150) NOT NULL,
  Start_Date DATE,
  End_Date DATE,
  Notes TEXT,
  Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  Updated_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  FOREIGN KEY (User_ID) REFERENCES User(User_ID)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- =========================================================
-- MEAL PLAN RECIPES (FINAL)
-- =========================================================
CREATE TABLE MealPlan_Recipes (
  MPR_ID INT AUTO_INCREMENT PRIMARY KEY,
  MealPlan_ID INT NOT NULL,
  Recipe_ID INT NOT NULL,
  Meal_Type ENUM('Breakfast','Lunch','Dinner','Snack'),
  Day_Of_Week VARCHAR(16),
  Sort_Order INT DEFAULT 0,
  Added_On DATETIME DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (MealPlan_ID) REFERENCES Meal_Plan(MealPlan_ID)
    ON DELETE CASCADE ON UPDATE CASCADE,

  FOREIGN KEY (Recipe_ID) REFERENCES Recipe(Recipe_ID)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- =========================================================
-- FEEDBACK TABLE
-- =========================================================
CREATE TABLE Feedback (
  Feedback_ID INT AUTO_INCREMENT PRIMARY KEY,
  User_ID INT NOT NULL,
  Recipe_ID INT NOT NULL,
  Rating TINYINT UNSIGNED NOT NULL CHECK (Rating BETWEEN 1 AND 5),
  Comments TEXT,
  Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  Updated_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  FOREIGN KEY (User_ID) REFERENCES User(User_ID)
    ON DELETE CASCADE ON UPDATE CASCADE,

  FOREIGN KEY (Recipe_ID) REFERENCES Recipe(Recipe_ID)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- =========================================================
-- LOG TABLES
-- =========================================================
CREATE TABLE Recipe_Log (
  Log_ID INT AUTO_INCREMENT PRIMARY KEY,
  Recipe_ID INT,
  Recipe_Name VARCHAR(200),
  Created_By INT,
  Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE User_Weight_History (
  History_ID INT AUTO_INCREMENT PRIMARY KEY,
  User_ID INT,
  Old_Weight DECIMAL(5,2),
  New_Weight DECIMAL(5,2),
  Updated_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (User_ID) REFERENCES User(User_ID)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- =========================================================
-- TRIGGERS
-- =========================================================
DELIMITER //
CREATE TRIGGER trg_after_recipe_insert
AFTER INSERT ON Recipe
FOR EACH ROW
BEGIN
  INSERT INTO Recipe_Log (Recipe_ID, Recipe_Name, Created_By)
  VALUES (NEW.Recipe_ID, NEW.Recipe_Name, NEW.Creator_User_ID);
END;
//

CREATE TRIGGER trg_update_bmi
BEFORE UPDATE ON User
FOR EACH ROW
BEGIN
  IF NEW.Height_cm IS NOT NULL AND NEW.Weight_kg IS NOT NULL THEN
    SET NEW.BMI = ROUND(NEW.Weight_kg / POW(NEW.Height_cm / 100, 2), 2);
  END IF;
END;
//
DELIMITER ;

-- =========================================================
-- FUNCTIONS
-- =========================================================
DELIMITER //
CREATE FUNCTION CalculateBMI(height_cm DECIMAL(6,2), weight_kg DECIMAL(6,2))
RETURNS DECIMAL(5,2)
DETERMINISTIC
BEGIN
  IF height_cm <= 0 THEN RETURN NULL; END IF;
  RETURN ROUND(weight_kg / POW(height_cm/100,2), 2);
END;
//

CREATE FUNCTION GetRecipeCalories(recipeId INT)
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
  DECLARE total DECIMAL(10,2);

  SELECT SUM((n.Calories / 100) * ri.Quantity)
  INTO total
  FROM Recipe_Ingredient ri
  JOIN Nutrition n ON n.Ingredient_ID = ri.Ingredient_ID
  WHERE ri.Recipe_ID = recipeId;

  RETURN IFNULL(total,0);
END;
//
DELIMITER ;

-- =========================================================
-- STORED PROCEDURES
-- =========================================================
DELIMITER //
CREATE PROCEDURE GetMealPlanSummary(IN userId INT)
BEGIN
  SELECT 
    mp.Plan_Name,
    mpr.Day_Of_Week,
    mpr.Meal_Type,
    r.Recipe_Name,
    GetRecipeCalories(r.Recipe_ID) AS Calories
  FROM Meal_Plan mp
  JOIN MealPlan_Recipes mpr ON mp.MealPlan_ID = mpr.MealPlan_ID
  JOIN Recipe r ON r.Recipe_ID = mpr.Recipe_ID
  WHERE mp.User_ID = userId
  ORDER BY mpr.Day_Of_Week, mpr.Meal_Type;
END;
//

CREATE PROCEDURE AddFeedback(
  IN p_userId INT,
  IN p_recipeId INT,
  IN p_rating TINYINT,
  IN p_comments TEXT
)
BEGIN
  INSERT INTO Feedback (User_ID, Recipe_ID, Rating, Comments, Date)
  VALUES (p_userId, p_recipeId, p_rating, p_comments, NOW());
END;
//

CREATE PROCEDURE UpdateUserWeight(
  IN p_userId INT,
  IN p_newWeight DECIMAL(5,2)
)
BEGIN
  DECLARE oldWeight DECIMAL(5,2);

  SELECT Weight_kg INTO oldWeight
  FROM User
  WHERE User_ID = p_userId;

  UPDATE User SET Weight_kg = p_newWeight
  WHERE User_ID = p_userId;

  INSERT INTO User_Weight_History(User_ID, Old_Weight, New_Weight)
  VALUES (p_userId, oldWeight, p_newWeight);
END;
//
DELIMITER ;

-- If you previously created a simpler MealPlan_Recipes table, add columns:
ALTER TABLE MealPlan_Recipes
  ADD COLUMN IF NOT EXISTS Meal_Type VARCHAR(32) DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS Day_Of_Week VARCHAR(16) DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS Sort_Order INT DEFAULT 0;









USE NutritionDB;

-- =========================================================
-- USERS
-- =========================================================
INSERT INTO User (Name, Email, Password, Gender, Date_Of_Birth, Height_cm, Weight_kg, Activity_Level, Dietary_Preferences, Allergies, role)
VALUES
('Alice Johnson', 'alice@example.com', 'alice123', 'Female', '1995-04-10', 165, 60.5, 'Moderate', 'Vegetarian', 'Peanuts', 'user'),
('Bob Smith', 'bob@example.com', 'bob123', 'Male', '1992-11-22', 178, 75.0, 'Active', 'Non-Vegetarian', NULL, 'user'),
('Charlie Green', 'charlie@example.com', 'charlie123', 'Other', '1998-01-14', 172, 68.0, 'Light', 'Vegan', 'Gluten', 'user'),
('Admin User', 'admin@nutrition.com', 'admin123', 'Male', '1988-09-01', 180, 78.5, 'Active', NULL, NULL, 'admin');


-- =========================================================
-- INGREDIENTS
-- =========================================================
INSERT INTO Ingredient (Ingredient_Name, Unit_Of_Measure, Category, Notes)
VALUES
('Chicken Breast', 'grams', 'Protein', 'Lean meat'),
('Broccoli', 'grams', 'Vegetable', 'High in fiber'),
('Brown Rice', 'grams', 'Grain', 'Complex carbohydrate'),
('Olive Oil', 'ml', 'Fat', 'Healthy fat source'),
('Tofu', 'grams', 'Protein', 'Soy-based protein'),
('Almonds', 'grams', 'Nuts', 'Contains healthy fats'),
('Apple', 'grams', 'Fruit', 'Rich in vitamins'),
('Egg', 'pieces', 'Protein', 'High-quality protein source'),
('Spinach', 'grams', 'Vegetable', 'Rich in iron'),
('Milk', 'ml', 'Dairy', 'Calcium source');

-- =========================================================
-- NUTRITION INFO
-- =========================================================
INSERT INTO Nutrition (Ingredient_ID, Calories, Carbohydrates_g, Protein_g, Fat_g, Fiber_g, Vitamins, Minerals)
VALUES
(1, 165, 0, 31, 3.6, 0, 'B6', 'Iron'),
(2, 55, 11.2, 3.7, 0.6, 5.1, 'C', 'Calcium'),
(3, 111, 23, 2.6, 0.9, 1.8, 'B', 'Magnesium'),
(4, 119, 0, 0, 13.5, 0, 'E', 'Zinc'),
(5, 76, 1.9, 8.0, 4.8, 0.3, 'B1', 'Iron'),
(6, 579, 21.6, 21.1, 49.9, 12.5, 'E', 'Magnesium'),
(7, 52, 14, 0.3, 0.2, 2.4, 'C', 'Potassium'),
(8, 78, 0.6, 6.3, 5.3, 0, 'B12', 'Zinc'),
(9, 23, 3.6, 2.9, 0.4, 2.2, 'A', 'Iron'),
(10, 42, 5, 3.4, 1, 0, 'D', 'Calcium');

-- =========================================================
-- RECIPES
-- =========================================================
INSERT INTO Recipe (Recipe_Name, Description, Cuisine_Type, Preparation_Time_minutes, Cooking_Time_minutes, Serving_Size, Difficulty_Level, Instructions, Creator_User_ID)
VALUES
('Grilled Chicken with Broccoli', 'Healthy high-protein meal with vegetables', 'Western', 15, 20, 1, 'Easy', 'Grill chicken and steam broccoli.', 1),
('Vegan Tofu Stir Fry', 'Delicious vegan-friendly tofu dish', 'Asian', 10, 15, 1, 'Medium', 'Stir fry tofu with spinach and olive oil.', 3),
('Brown Rice with Egg', 'Balanced carb-protein meal', 'Indian', 10, 25, 2, 'Easy', 'Cook brown rice and top with boiled eggs.', 2),
('Oatmeal with Milk and Apple', 'Quick healthy breakfast', 'Continental', 5, 5, 1, 'Easy', 'Mix milk with oats and add apple slices.', 1);

-- =========================================================
-- RECIPE_INGREDIENT RELATION
-- =========================================================
INSERT INTO Recipe_Ingredient (Recipe_ID, Ingredient_ID, Quantity, Unit)
VALUES
(1, 1, 200, 'grams'),
(1, 2, 100, 'grams'),
(2, 5, 150, 'grams'),
(2, 9, 50, 'grams'),
(2, 4, 10, 'ml'),
(3, 3, 200, 'grams'),
(3, 8, 2, 'pieces'),
(4, 10, 200, 'ml'),
(4, 7, 100, 'grams');

-- =========================================================
-- MEAL PLANS
-- =========================================================
INSERT INTO Meal_Plan (User_ID, Plan_Name, Start_Date, End_Date, Notes)
VALUES
(1, 'Alice Healthy Plan', '2025-11-01', '2025-11-07', 'High protein focus'),
(2, 'Bob Weight Gain', '2025-11-02', '2025-11-09', 'Increased calorie intake'),
(3, 'Charlie Vegan Diet', '2025-11-03', '2025-11-10', 'Plant-based nutrition');

-- =========================================================
-- MEALPLAN_RECIPE LINK
-- =========================================================
INSERT INTO MealPlan_Recipe (MealPlan_ID, Recipe_ID, Day_of_Plan, Meal_Type)
VALUES
(1, 1, '2025-11-01', 'Lunch'),
(1, 4, '2025-11-02', 'Breakfast'),
(2, 3, '2025-11-03', 'Dinner'),
(3, 2, '2025-11-04', 'Lunch');

-- =========================================================
-- USER DIET LOG
-- =========================================================
INSERT INTO User_Diet_Log (User_ID, Recipe_ID, Date, Time, Portion_Size, Notes, is_finished)
VALUES
(1, 1, '2025-11-01', '12:30:00', 1, 'Post-workout meal', TRUE),
(1, 4, '2025-11-02', '08:00:00', 1, 'Morning breakfast', TRUE),
(2, 3, '2025-11-03', '20:00:00', 2, 'Dinner before gym', TRUE),
(3, 2, '2025-11-04', '13:00:00', 1, 'Vegan lunch', TRUE);

-- =========================================================
-- FEEDBACK
-- =========================================================
INSERT INTO Feedback (User_ID, Recipe_ID, Rating, Comments)
VALUES
(1, 1, 5, 'Loved the grilled chicken!'),
(2, 3, 4, 'Tasty but needed more flavor.'),
(3, 2, 5, 'Perfect vegan option!'),
(1, 4, 4, 'Good breakfast idea.');

-- =========================================================
-- USER WEIGHT HISTORY
-- =========================================================
INSERT INTO User_Weight_History (User_ID, Old_Weight, New_Weight)
VALUES
(1, 61.0, 60.5),
(2, 74.0, 75.0),
(3, 69.0, 68.0);

-- =========================================================
-- END OF SCRIPT
-- =========================================================