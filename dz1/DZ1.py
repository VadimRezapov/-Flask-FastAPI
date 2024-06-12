from flask import Flask, url_for, render_template

app = Flask(__name__)


@app.route('/')
def start():
    return render_template('index.html')


@app.route('/jeans/')
def jeans():
    jeans_block = [
        {'type': 'Джинсы Levis',
         'cost': '8 400.00',
         'pict': url_for('static', filename='jeans1.png')},
        {'type': 'Джинсы Barouz',
         'cost': '1 800.00',
         'pict': url_for('static', filename='jeans2.png')},
        {'type': 'Джинсы RACCOON',
         'cost': '2 200.00',
         'pict': url_for('static', filename='jeans3.png')},
        {'type': 'Джинсы Lee Brooklyn Dark Stonewash',
         'cost': '4 800.00',
         'pict': url_for('static', filename='jeans4.png')},
        {'type': 'Джинсы  Добрыня Лето',
         'cost': '1 500.00',
         'pict': url_for('static', filename='jeans5.png')},
        ]
    return render_template('jeans.html', content_block=jeans_block)


@app.route('/jacket/')
def jacket():
    jacket_block = [
        {'type': 'Куртка adidas Sportswear M Prsve Boa Jk',
         'cost': '3 400.00',
         'pict': url_for('static', filename='jacket1.png')},
        {'type': 'Куртка PUMA Mid X-Tricot Down Jacket',
         'cost': '10 800.00',
         'pict': url_for('static', filename='jacket2.png')},
        {'type': 'Куртка H&M',
         'cost': '4 600.00',
         'pict': url_for('static', filename='jacket3.png')},
        {'type': 'Куртка Mege Knight',
         'cost': '5 200.00',
         'pict': url_for('static', filename='jacket4.png')},
        {'type': 'Куртка кожанная Qors',
         'cost': '6 100.00',
         'pict': url_for('static', filename='jacket5.png')}
    ]
    return render_template('jacket.html', content_block=jacket_block)


@app.route('/shoes/')
def shoes():
    shoes_block = [
        {'type': 'Кроссовки мужские Demix Compact 6',
         'cost': '5 600.00',
         'pict': url_for('static', filename='shoes1.png')},
        {'type': 'Сандалии мужские Outventure Trackerи',
         'cost': '1 300.00',
         'pict': url_for('static', filename='shoes2.png')},
        {'type': 'Кроссовки мужские Termit City Rock',
         'cost': '6 500.00',
         'pict': url_for('static', filename='shoes3.png')},
        {'type': 'Ботинки утепленные мужские Northland Graz Winter 200 Waterguard',
         'cost': '9 300.00',
         'pict': url_for('static', filename='shoes4.png')},
        {'type': 'Полуботинки Caterpillar Ventura',
         'cost': '7 900.00',
         'pict': url_for('static', filename='shoes5.png')}
    ]
    return render_template('shoes.html', content_block=shoes_block)


if __name__ == '__main__':
    app.run(debug=True)