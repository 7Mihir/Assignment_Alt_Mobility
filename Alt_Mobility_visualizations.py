#!/usr/bin/env python
# coding: utf-8

# In[34]:


import pandas as pd
import matplotlib.pyplot as plt

# Load data
orders = pd.read_csv('customer_orders.csv', parse_dates=['order_date'])
payments = pd.read_csv('payments.csv', parse_dates=['payment_date'])

# Preprocess
orders['order_month'] = orders['order_date'].values.astype('datetime64[M]')
payments['payment_month'] = payments['payment_date'].values.astype('datetime64[M]')



# In[51]:


# Visualization 1: Order Status Distribution
status_counts = orders['order_status'].value_counts()
plt.figure()
bars = plt.bar(status_counts.index, status_counts.values)
plt.xlabel('Order Status')
plt.ylabel('Count')
plt.title('Order Status Distribution')
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval, int(yval), va='bottom', ha='center')
plt.tight_layout()
plt.show()



# In[52]:


# Visualization 2: Monthly Total Orders
monthly_orders = orders.groupby('order_month').size()
plt.figure()
plt.plot(monthly_orders.index, monthly_orders.values,marker='o')
plt.xlabel('Year-Month')
plt.ylabel('Total Orders')
plt.title('Monthly Total Orders')
plt.tight_layout()
plt.show()


# In[53]:


# Visualization 3: Monthly Total Revenue
monthly_revenue = orders.groupby('order_month')['order_amount'].sum()
plt.figure()
plt.plot(monthly_revenue.index, monthly_revenue.values,marker='o')
plt.xlabel('Year-Month')
plt.ylabel('Total Revenue')
plt.title('Monthly Total Revenue')
plt.tight_layout()
plt.show()


# In[38]:


# Visualization 4: Revenue by Order Status
rev_by_status = orders.groupby('order_status')['order_amount'].sum()
plt.figure()
bars = plt.bar(rev_by_status.index, rev_by_status.values)
plt.xlabel('Order Status')
plt.ylabel('Revenue')
plt.title('Revenue by Order Status')
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.0f}', va='bottom', ha='center')
plt.tight_layout()
plt.show()


# In[39]:


# Visualization 5: Top 20 Customers by Order Count
cust_counts = orders['customer_id'].value_counts().head(20)
plt.figure(figsize=(12,6))
bars = plt.bar(cust_counts.index.astype(str), cust_counts.values)
plt.xlabel('Customer ID')
plt.ylabel('Number of Orders')
plt.title('Top 20 Customers by Order Count')
plt.xticks(rotation=90)
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval, int(yval), va='bottom', ha='center')
plt.tight_layout()
plt.show()


# In[11]:


# Visualization 6: Customer Segments
order_freq = orders.groupby('customer_id').size()
segments = pd.cut(order_freq, bins=[0,1,4,float('inf')], labels=['One-time','Occasional','Frequent'])
seg_counts = segments.value_counts().loc[['One-time','Occasional','Frequent']]
plt.figure()
bars = plt.bar(seg_counts.index, seg_counts.values)
plt.xlabel('Customer Segment')
plt.ylabel('Number of Customers')
plt.title('Customer Segments by Order Frequency')
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval, int(yval), va='bottom', ha='center')
plt.tight_layout()
plt.show()


# In[54]:


# Visualization 7: Monthly New vs Returning Customers
first_order = orders.groupby('customer_id')['order_month'].min().reset_index().rename(columns={'order_month':'first_month'})
orders2 = orders.merge(first_order, on='customer_id')
monthly_new = orders2[orders2['order_month'] == orders2['first_month']].groupby('order_month')['customer_id'].nunique()
monthly_ret = orders2[orders2['order_month'] > orders2['first_month']].groupby('order_month')['customer_id'].nunique()
monthly_df = pd.DataFrame({'new_customers': monthly_new, 'returning_customers': monthly_ret}).fillna(0)
plt.figure()
plt.plot(monthly_df.index, monthly_df['new_customers'],marker='o', label='New Customers')
plt.plot(monthly_df.index, monthly_df['returning_customers'], marker='o',label='Returning Customers')
plt.xlabel('year-Month')
plt.ylabel('Number of Customers')
plt.title('Monthly New vs Returning Customers')
plt.legend()
plt.tight_layout()
plt.show()


# In[18]:


# Visualization 8: Payment Status Distribution
pay_status_counts = payments['payment_status'].value_counts()
plt.figure()
bars = plt.bar(pay_status_counts.index, pay_status_counts.values)
plt.xlabel('Payment Status')
plt.ylabel('Count')
plt.title('Payment Status Distribution')
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval, int(yval), va='bottom', ha='center')
plt.tight_layout()
plt.show()


# In[43]:


# Visualization 9: Success vs Failure Rate by Payment Method
pm = payments.groupby('payment_method').agg(
    total_txns=('payment_id', 'count'),
    success_rate=('payment_status', lambda x: (x == 'completed').sum() / x.size),
    failure_rate=('payment_status', lambda x: (x == 'failed').sum() / x.size)
)

plt.figure()
plt.plot(pm.index, pm['success_rate'], marker='o', label='Success Rate')
plt.plot(pm.index, pm['failure_rate'], marker='o', label='Failure Rate')

# Use .iloc[] to access the correct positions
for i, method in enumerate(pm.index):
    plt.text(i, pm['success_rate'].iloc[i], f'{pm["success_rate"].iloc[i]:.2f}', va='bottom', ha='center')
    plt.text(i, pm['failure_rate'].iloc[i], f'{pm["failure_rate"].iloc[i]:.2f}', va='top', ha='center')

plt.xlabel('Payment Method')
plt.ylabel('Rate')
plt.title('Success vs Failure Rate by Payment Method')
plt.legend()
plt.tight_layout()
plt.show()


# In[56]:


# Visualization 10: Monthly Failed vs Successful Payments
pm_monthly = payments.groupby('payment_month').agg(
    failed=('payment_status', lambda x: (x=='failed').sum()),
    success=('payment_status', lambda x: (x=='completed').sum())
)
plt.figure()
plt.plot(pm_monthly.index, pm_monthly['failed'],label='Failed Payments')
plt.plot(pm_monthly.index, pm_monthly['success'],label='Successful Payments')
plt.xlabel('Year Month')
plt.ylabel('Count')
plt.title('Monthly Failed vs Successful Payments')
plt.legend()
plt.tight_layout()
plt.show()


# In[57]:


orders = pd.read_csv('customer_orders.csv', parse_dates=['order_date'])
orders['order_month'] = orders['order_date'].dt.to_period('M').dt.to_timestamp()

cohort = orders.groupby('customer_id')['order_month'].min().reset_index()
cohort.columns = ['customer_id', 'cohort_month']

orders = orders.merge(cohort, on='customer_id')

orders['months_since_cohort'] = (
    (orders['order_month'].dt.year - orders['cohort_month'].dt.year) * 12 +
    (orders['order_month'].dt.month - orders['cohort_month'].dt.month)
)

cohort_data = orders.groupby(['cohort_month', 'months_since_cohort'])['customer_id'].nunique().reset_index()

cohort_sizes = cohort_data[cohort_data['months_since_cohort'] == 0][['cohort_month', 'customer_id']].set_index('cohort_month')
cohort_sizes.columns = ['cohort_size']

retention = cohort_data.pivot(index='cohort_month', columns='months_since_cohort', values='customer_id')
retention = retention.divide(cohort_sizes['cohort_size'], axis=0).round(3)

retention = retention.loc['2023-01-01':'2023-06-01', :13]  # adjust as needed

plt.figure(figsize=(12, 6))
plt.imshow(retention, cmap='Blues', aspect='auto')
plt.colorbar(label='Retention Rate')
plt.title('Customer Retention Heatmap (Cohort Analysis)')
plt.xlabel('Months Since First Purchase')
plt.ylabel('Cohort Month')

plt.xticks(ticks=range(retention.columns.shape[0]), labels=[f'Month {i}' for i in retention.columns])
plt.yticks(ticks=range(retention.shape[0]), labels=[index.strftime('%Y-%m') for index in retention.index])

for i in range(retention.shape[0]):
    for j in range(retention.shape[1]):
        value = retention.iloc[i, j]
        if pd.notnull(value):
            plt.text(j, i, f'{value:.2f}', ha='center', va='center', color='black')

plt.tight_layout()
plt.show()


# In[ ]:




