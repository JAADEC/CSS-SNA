library(ggplot2)
library(tidyr)
library(readxl)

ei_try <- read_xlsx("C:/Users/walke/Downloads/Gephi_pull_eig.xlsx")

View(ei_try)


#this is to plot histo-density plots in order to see if there is a canon
class(ei_try$eig_centrality)  # Likely returns "character" or "factor"
ei_try$eig_centrality <- as.numeric(ei_try$eig_centrality)

eig_dist_plot <- ggplot(ei_try, aes(x = eig_centrality)) +
  geom_histogram(bins = 30, fill = "skyblue", color = "black") +
  labs(title = "Distribution of Eigenvector Centrality",
       x = "Eigenvector Centrality", y = "Frequency") +
  theme_minimal()

eig_dense_plot <- ggplot(ei_try, aes(x = eig_centrality)) +
  geom_density(fill = "orange", alpha = 0.5) +
  labs(title = "Density Plot of Eigenvector Centrality",
       x = "Eigenvector Centrality", y = "Density") +
  theme_minimal()

eig_dist_plot
eig_dense_plot

mean(ei_try$eig_centrality)


# Plot on log-log scale (to check if power law is correct)
#plot(rank, ranked_evc, log = "xy", pch = 20, col = "blue",
    # xlab = "Rank (log)", ylab = "Eigenvector Centrality (log)",
     #main = "Log-Log Rank vs. EVC")







# elbows - this is for identifying the canon from the influential, etc. --------
# Copy the original dataframe
ei_labeled <- ei_try

?inflection
# Sort eigenvector values (descending)
eig_vals <- sort(ei_labeled$eig_centrality, decreasing = TRUE)

# Get elbows
library(inflection)
inflections <- findiplist(1:length(eig_vals), eig_vals, index = TRUE)
elbow1 <- inflections[1]
elbow2 <- if (length(inflections) > 1) inflections[2] else NA

# Extract thresholds from the sorted eig_vals
# Ensure correct order: threshold_high >= threshold_mid >= threshold_low
thresholds <- sort(c(eig_vals[elbow1], eig_vals[elbow2]), decreasing = TRUE)
threshold1 <- thresholds[1]  # upper threshold (for "Canon")
threshold2 <- thresholds[2]  # lower threshold (for "Influential")

# Initialize column
ei_labeled$canon_type <- "Normal"

# Assign Canon
ei_labeled$canon_type[ei_labeled$eig_centrality >= threshold1] <- "Canon"

# Assign Influential
ei_labeled$canon_type[ei_labeled$eig_centrality < threshold1 &
                        ei_labeled$eig_centrality >= threshold2] <- "Influential"


View(ei_labeled)

plot(eig_vals, type = "l", main = "Eigenvector Centrality with Elbow Points",
     xlab = "Rank", ylab = "Eigenvector Centrality")
abline(v = c(elbow1, elbow2), col = c("red", "blue"), lty = 2)
legend("topright", legend = c("1st Elbow", "2nd Elbow"), col = c("red", "blue"), lty = 2)


mean(eig_vals)


# category displays -------------------------------------------------------

# Ensure all categories are present by defining factor levels
ei_labeled$Canon_type <- factor(ei_labeled$Canon_type,
                                levels = c("Canon", "Influential", "Normal"))

# Count and calculate percentages
category_counts <- table(ei_labeled$Canon_type)
category_percent <- prop.table(category_counts) * 100
category_percent_rounded <- round(category_percent, 1)

# Display result
category_percent_rounded

print(elbow2)

# Create labels for the pie chart
labels <- paste(names(category_percent_rounded),
                "-", category_percent_rounded, "%")

# Draw pie chart
pie(category_percent, labels = labels,
    col = c("gold", "skyblue", "lightgrey"),
    main = "Influence Breakdown - Whole CA Network")


# check skew --------------------------------------------------------------

# Install if needed
install.packages("moments")

# Load the package
library(moments)

# Calculate skewness of your vector, e.g., eig_centrality
skew_val <- skewness(ei_try$eig_centrality, na.rm = TRUE)

print(skew_val)


# citation ----------------------------------------------------------------

# Sum of citations for Canon category
canon_citations <- sum(ei_labeled$Cited_by[ei_labeled$canon_type == "Canon"], na.rm = TRUE)

# Sum of citations for all works
total_citations <- sum(ei_labeled$Cited_by, na.rm = TRUE)

# Percentage of citations from Canon category
percent_canon_citations <- (canon_citations / total_citations) * 100

# Print result
print(paste0("Canon category accounts for ", round(percent_canon_citations, 2), "% of total citations."))

# Count works in Canon category
canon_count <- sum(ei_labeled$canon_type == "Canon", na.rm = TRUE)

# Print result
print(paste("Number of works in Canon category:", canon_count))




# power-law check ---------------------------------------------------------

ranked_evc <- sort(evc, decreasing = TRUE)
rank <- 1:length(ranked_evc)

plot(rank, ranked_evc, log = "xy", pch = 20,
     main = "Log-Log plot of Rank vs. Eigenvector Centrality",
     xlab = "Rank", ylab = "Eigenvector Centrality")

library(dplyr) # Make sure dplyr is loaded for the filter function


# p-law for cluster 0 -----------------------------------------------------

library(dplyr) # For data manipulation
library(ggplot2) # Optional: for more flexible plotting, but base R plot will work too

# Assuming ei_labeled is your dataframe with 'eig_centrality' and 'Mod_class' columns

# Get unique Mod_class values and sort them, or define them explicitly
# mod_classes_to_plot <- unique(ei_labeled$Mod_class) %>% sort()
# If you specifically want 0 to 7, define it:
mod_classes_to_plot <- 0:7

# Loop through each Mod_class
for (m_class in mod_classes_to_plot) {
  
  # 1. Filter the data for the current Mod_class
  ei_filtered <- ei_labeled %>%
    filter(Mod_class == m_class)
  
  # Check if there's any data for this Mod_class before proceeding
  if (nrow(ei_filtered) == 0) {
    message(paste("No data for Mod_class =", m_class, ". Skipping plot."))
    next # Skip to the next iteration of the loop
  }
  
  # 2. Extract and sort the eig_centrality values from the filtered data
  #    Ensure eig_centrality is numeric and handle potential NAs if any
  eig_values_to_plot <- as.numeric(as.character(ei_filtered$eig_centrality)) # Convert if needed
  eig_values_to_plot <- eig_values_to_plot[!is.na(eig_values_to_plot)] # Remove NAs
  
  # Check if there are still values after NA removal
  if (length(eig_values_to_plot) == 0) {
    message(paste("No valid numeric eig_centrality values for Mod_class =", m_class, ". Skipping plot."))
    next # Skip to the next iteration
  }
  
  ranked_eig_centrality <- sort(eig_values_to_plot, decreasing = TRUE)
  
  # 3. Create the rank vector based on the filtered data's length
  rank_vec <- 1:length(ranked_eig_centrality)
  
  # 4. Generate the plot
  # Optional: You might want to save each plot to a file if you have many
  # For example, using pdf() or png():
  # pdf(paste0("rank_eig_centrality_Mod_class_", m_class, ".pdf"))
  
  plot(rank_vec, ranked_eig_centrality, log = "xy", pch = 20,
       main = paste("Log-Log Plot of Rank vs. Eigenvector Centrality\n(Mod_class =", m_class, ")"),
       xlab = "Rank", ylab = "Eigenvector Centrality")
  
  # If you opened a PDF/PNG device, remember to close it
  # dev.off()
}

# Optional: You can also use ggplot2 for a single plot with facets, which can be cleaner
# This requires installing ggplot2: install.packages("ggplot2")

# First, ensure eig_centrality is numeric in the original dataframe
ei_labeled_clean <- ei_labeled %>%
  mutate(eig_centrality = as.numeric(as.character(eig_centrality))) %>%
  filter(!is.na(eig_centrality)) # Remove NAs from the whole column upfront

# Calculate ranks within each Mod_class
ranked_data_for_plot <- ei_labeled_clean %>%
  filter(Mod_class %in% mod_classes_to_plot) %>% # Filter to only the classes you want to plot
  group_by(Mod_class) %>%
  arrange(desc(eig_centrality)) %>% # Arrange within each group by eig_centrality
  mutate(rank = row_number()) # Assign rank within each group

# Plot using ggplot2 with facets
ggplot(ranked_data_for_plot, aes(x = rank, y = eig_centrality)) +
  geom_point(shape = 20) +
  scale_x_log10() + # Log scale for X-axis
  scale_y_log10() + # Log scale for Y-axis
  facet_wrap(~ Mod_class, scales = "free") + # Create separate plots for each Mod_class
  labs(
    title = "Log-Log Plot of Rank vs. Eigenvector Centrality by Mod_class",
    x = "Rank",
    y = "Eigenvector Centrality"
  ) +
  theme_minimal() # Or theme_bw()





install.packages("poweRlaw")  # if not already installed
library(poweRlaw)



evc <- as.numeric(ei_labeled$eig_centrality)
evc <- evc[evc > 0]  # Power-law applies to positive values only

pl_model <- conpl$new(evc)

# Estimate xmin (lower bound where power-law behavior starts)
est <- estimate_xmin(pl_model)
pl_model$setXmin(est)

# Show estimated xmin and alpha (power-law exponent)
print(pl_model)


gof <- bootstrap_p(pl_model, no_of_sims=1000, threads=2)  # adjust sims for speed

print(gof$p)  # p-value for power-law fit



# conflict types ----------------------------------------------------------

# Define your conflict columns
conflict_cols <- c("Insurgency", "Uprising", "Unrest", "Civil War", "Rebellion", "Revolution")

# Create a new column combining the conflict types present in each row
ei_try$conflict_combination <- apply(ei_try[, conflict_cols], 1, function(row) {
  conflicts <- conflict_cols[row == 1]
  if (length(conflicts) == 0) {
    return("None")
  } else {
    return(paste(conflicts, collapse = "+"))
  }
})

# Calculate frequency table
combination_counts <- table(ei_try$conflict_combination)

# Convert to dataframe for easier manipulation
df_comb <- as.data.frame(combination_counts)
colnames(df_comb) <- c("Combination", "Count")

# Lump small-frequency combinations into "Other"
df_comb$Combination <- as.character(df_comb$Combination)  # ensure it's character type

df_comb$Combination <- ifelse(df_comb$Count <= 18, "Other", df_comb$Combination)

# Aggregate counts after lumping
df_comb_agg <- aggregate(Count ~ Combination, data = df_comb, sum)

# Base R pie chart
pie(df_comb_agg$Count, labels = df_comb_agg$Combination,
    main = "Distribution of Conflict Type Combinations (18 or fewer lumped)",
    col = rainbow(nrow(df_comb_agg)))

# ggplot2 pie chart
library(ggplot2)

ggplot(df_comb_agg, aes(x = "", y = Count, fill = Combination)) +
  geom_col(width = 1) +
  coord_polar(theta = "y") +
  theme_void() +
  labs(title = "Distribution of Conflict Type Combinations (18 or fewer lumped)") +
  theme(legend.position = "right")

View(df_comb_agg)
View(combination_counts)

print(combination_counts)




# attempt 2 conflict type -------------------------------------------------

# Define your conflict columns
conflict_cols <- c("Insurgency", "Uprising", "Unrest", "Civil War", "Rebellion", "Revolution")

# Count how many papers have a 1 in each category
conflict_counts <- colSums(ei_try[, conflict_cols] == 1, na.rm = TRUE)

# Calculate total number of papers (rows)
total_papers <- nrow(ei_try)

# Calculate percentages
conflict_percentages <- (conflict_counts / total_papers) * 100

# Combine counts and percentages into a data frame
conflict_summary <- data.frame(
  Conflict_Type = conflict_cols,
  Count = conflict_counts,
  Percentage = round(conflict_percentages, 2)
)

print(conflict_summary)


library(ggplot2)

# Assuming you already have conflict_summary from before

# Basic bar plot of counts with percentages as labels
ggplot(conflict_summary, aes(x = Conflict_Type, y = Count, fill = Conflict_Type)) +
  geom_col(show.legend = FALSE) +
  geom_text(aes(label = paste0(Percentage, "%")), vjust = -0.5) +  # show percentages above bars
  labs(title = "Number of Papers by Conflict Type",
       x = "Conflict Type",
       y = "Count of Papers") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

unique(ei_labeled$Mod_class)





# Breakdown by cluster ----------------------------------------------------
library(ggplot2)
library(dplyr)

# Calculate counts of each Mod_class value
modclass_counts <- table(ei_labeled$Mod_class)

modclass_labels <- as.data.frame(modclass_counts)


# Convert to data frame
df_modclass <- as.data.frame(modclass_counts)
colnames(df_modclass) <- c("Mod_class", "Count")

# Calculate total rows
total_rows <- nrow(ei_labeled)

# Calculate percentages
df_modclass$Percentage <- round((df_modclass$Count / total_rows) * 100, 2)

# Reorder Mod_class factor by Count descending for largest slices first
df_modclass <- df_modclass %>%
  arrange(desc(Count)) %>%
  mutate(
    Mod_class = factor(Mod_class, levels = Mod_class),  # reorder factor by Count descending
    label = paste0(Mod_class, "\n", Percentage, "%")    # label with Mod_class and percentage
  )

# # Pie chart with clockwise slices and labels on slices
# ggplot(df_modclass, aes(x = "", y = Count, fill = Mod_class)) +
#   geom_col(width = 1, color = "white") +
#   coord_polar(theta = "y", direction = -1) +    # direction = -1 for clockwise order
#   geom_text(aes(label = label), 
#             position = position_stack(vjust = .5), size = 3, color = "white") +
#   labs(title = "The CA Approach to Conflict (Literature % by Cluster)", fill = 'Clusters') +
#   theme_void() +
#   theme(legend.position = "right") +
#   scale_fill_discrete(labels = c("0 - Greed Studies of Civil War", "1 - Autocratic Survival", "2 - Institutions, regimes, & economic growth", "3 - Public choice theories of rebellion", "4 - Climate, Exogenous Shocks, & conflict", "5 - Methodology, mechanisms, & the limits of RCT", "6 - Civil Conflict", "7 - Bargaining Theories of Civil War"))# Hide legend because labels are on slices



# Define your custom color palette (one hex code per Mod_class in order 0-7)
library(ggplot2)
install.packages("showtext")
library(showtext) # For custom fonts

# Load Libertinus Serif (must be installed on your system first)
font_add("Libertinus Serif", regular = "C:\\Users\\walke\\Downloads\\Libertinus-7.051\\Libertinus-7.051\\static\\TTF\\LibertinusSerif-Regular.ttf")
showtext_auto()

# Apply to your pie chart legend




custom_colors <- c(
  "0" = "#73c000",  # Greed Studies
  "1" = "#ff5584",  # Autocratic Survival
  "2" = "#e072ff",  # Institutions
  "3" = "#fffb08",  # Public Choice
  "4" = "#00c4ff",  # Climate
  "5" = "#ffdbbd",  # Methodology
  "6" = "#2334ff",  # Civil Conflict
  "7" = "#ff9158"   # Bargaining Theories
)

pie <- ggplot(df_modclass, aes(x = "", y = Count, fill = factor(Mod_class))) +
  geom_col(width = 1, color = "black") +
  coord_polar(theta = "y", direction = -1) +
  geom_text(aes(label = label), 
            position = position_stack(vjust = .5),
            family = "Libertinus Serif",
            size = 3, color = "black") +
  labs(title = "The CA Approach to Conflict (Literature % by Cluster)", 
       fill = 'Legend') +
  theme_void() +
  theme(legend.position = "right") +
  scale_fill_manual(
    values = custom_colors,
    labels = c("0 - Greed Studies of Civil War", 
               "1 - Autocratic Survival", 
               "2 - Institutions, regimes, & economic growth", 
               "3 - Public choice theories of rebellion", 
               "4 - Climate, Exogenous Shocks, & conflict", 
               "5 - Methodology, mechanisms, & the limits of RCT", 
               "6 - Civil Conflict", 
               "7 - Bargaining Theories of Civil War")
  )

pie_chart <- pie +
  theme(
    # Add these lines to modify legend without affecting other theme elements
    legend.title = element_text(size = 15, face = "bold"),
    legend.text = element_text(size = 14),
    legend.key.size = unit(1, "cm"),
    legend.key = element_rect(color = "black", fill = "white")
  ) +
  guides(fill = guide_legend(
    override.aes = list(color = "black", size = 1),
    title.position = "top",
    label.position = "right"
  ))

theme(plot.title = element_text(hjust = 0.5))

print(pie_chart)

print(pie)

# Ensure Mod_class is treated as character for color matching
pie <- ggplot(df_modclass, aes(x = "", y = Count, 
                               fill = as.character(Mod_class))) +  # Changed to as.character
  geom_col(width = 1, color = "black") +
  coord_polar(theta = "y", direction = -1) +
  labs(fill = 'Legend') +
  theme_void() +
  theme(legend.position = "right") +
  scale_fill_manual(
    values = custom_colors,
    labels = c("0 - Greed Studies of Civil War", 
               "1 - Autocratic Survival", 
               "2 - Institutions, Regimes, & Economic Growth", 
               "3 - Public Choice Theories of Rebellion", 
               "4 - Climate, Exogenous Shocks, & Conflict", 
               "5 - Methodology, Mechanisms, & the Limits of RCT", 
               "6 - Civil Conflict", 
               "7 - Bargaining Theories of Civil War")
  )

pie + theme(
  legend.text = element_text(family = "Libertinus Serif", size = 25),
  legend.title = element_text(family = "Libertinus Serif", face = "bold", size = 30)
)




# cluster & conflict type -------------------------------------------------
library(dplyr)
library(ggplot2)
library(patchwork)

conflict_cols <- c("Insurgency", "Uprising", "Unrest", "Civil War", "Rebellion", "Revolution")

conflict_colors <- c(
  "Insurgency" = "#1f77b4",
  "Uprising" = "#ff7f0e",
  "Unrest" = "#2ca02c",
  "Civil War" = "#d62728",
  "Rebellion" = "#9467bd",
  "Revolution" = "#8c564b"
)

plots_list <- list()

for (cls in 0:7) {
  ei_mod <- ei_labeled %>% filter(Mod_class == cls)
  if (nrow(ei_mod) == 0) next
  
  conflict_counts <- colSums(ei_mod[, conflict_cols] == 1, na.rm = TRUE)
  total_mod <- nrow(ei_mod)
  conflict_percent <- (conflict_counts / total_mod) * 100
  
  conflict_summary <- data.frame(
    Conflict_Type = conflict_cols,
    Count = conflict_counts,
    Percentage = round(conflict_percent, 2)
  )
  
  # Reorder Conflict_Type factor by Count descending for bar order
  conflict_summary$Conflict_Type <- factor(conflict_summary$Conflict_Type,
                                           levels = conflict_summary$Conflict_Type[order(conflict_summary$Count, decreasing = TRUE)])
  
  # All percentages inside the bar with white text
  conflict_summary <- conflict_summary %>%
    mutate(
      label_vjust = 1,
      label_color = "white"
    )
  
  p <- ggplot(conflict_summary, aes(x = Conflict_Type, y = Count, fill = Conflict_Type)) +
    geom_col(show.legend = FALSE) +
    geom_text(aes(label = paste0(Percentage, "%"), vjust = label_vjust, color = label_color), size = 3) +
    scale_fill_manual(values = conflict_colors) +
    scale_color_identity() +  # Use label_color column as actual colors
    labs(title = paste("Conflict Types by Cluster", cls),
         x = NULL,
         y = "# of Papers") +
    theme_minimal() +
    theme(axis.text.x = element_text(angle = 45, hjust = 1))
  
  plots_list[[paste0("Mod_class_", cls)]] <- p
}

# Combine all plots with shared legend
combined_plot <- wrap_plots(plots_list, ncol = 2, guides = "collect") & 
  theme(legend.position = "bottom")

print(combined_plot)




# mean citations table ----------------------------------------------------

library(dplyr)

# Calculate mean citations per Mod_class
mean_citations_by_modclass <- ei_labeled %>%
  group_by(Mod_class) %>%
  summarise(
    Mean_Citations = mean(Cites, na.rm = TRUE),
    Count = n()
  ) %>%
  arrange(Mod_class)

# View the result
as.data.frame(mean_citations_by_modclass)


# mean ei centrality ------------------------------------------------------

ei_labeled$eig_centrality <- as.numeric(ei_labeled$eig_centrality)

mean_ei_by_modclass <- ei_labeled %>%
  group_by(Mod_class) %>%
  summarise(
    Mean_EI = mean(eig_centrality, trim = 0.10, na.rm = TRUE),
    Count = n()
  ) %>%
  arrange(Mod_class)

as.data.frame(mean_ei_by_modclass)
