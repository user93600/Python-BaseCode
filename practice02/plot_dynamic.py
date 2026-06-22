import matplotlib.pyplot as plt
import random

plt.ion()
data =[]

fig=plt.figure()
ax=fig.add_subplot(111)


for i in range(200):
    if not plt.fignum_exists(fig.number):
        break
    new_val=random.randint(0,100)
    data.append(new_val)
    if len(data)>20:
        data.pop(0)
    
    plt.clf()
    plt.plot(data)
    plt.ylim(0,100)
    plt.pause(0.01)

plt.ioff()
plt.show()