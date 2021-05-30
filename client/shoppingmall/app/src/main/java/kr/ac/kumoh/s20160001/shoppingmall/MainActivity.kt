package kr.ac.kumoh.s20160001.shoppingmall

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.core.graphics.drawable.toBitmap
import androidx.lifecycle.Observer
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.DefaultItemAnimator
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.android.volley.toolbox.NetworkImageView
import kotlinx.android.synthetic.main.activity_main.*
import com.bumptech.glide.Glide


class MainActivity : AppCompatActivity() {
    private lateinit var model: ViewModel
    private val mAdapter = ProductAdapter()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        product_list.apply {
            layoutManager = LinearLayoutManager(applicationContext)
            setHasFixedSize(true)
            itemAnimator = DefaultItemAnimator()
            adapter = mAdapter
        }

        model = ViewModelProvider(this,
            ViewModelProvider.AndroidViewModelFactory(application))
            .get(ViewModel::class.java)

        model.list.observe(this, Observer<ArrayList<ViewModel.Product>> {
            mAdapter.notifyDataSetChanged()
        })

        model.getInfo()

    }

    inner class ProductAdapter: RecyclerView.Adapter<ProductAdapter.ViewHolder>() {

        inner class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
            val txName = itemView.findViewById<TextView>(R.id.text1)
            val txPrice = itemView.findViewById<TextView>(R.id.text2)
            val productImg = itemView.findViewById<ImageView>(R.id.image)


        }

        override fun getItemCount(): Int {
            return model.getSize()
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ProductAdapter.ViewHolder {
            val view = layoutInflater.inflate(
                R.layout.cardview,
                parent,
                false)
            return ViewHolder(view)
        }

        override fun onBindViewHolder(holder: ProductAdapter.ViewHolder, position: Int) {
            holder.txName.text = model.getProduct(position).name
            holder.txPrice.text = model.getProduct(position).price
            model.setImg(model.getProduct(position).id,holder.productImg)

            holder.itemView.setOnClickListener(){
                val intent = Intent(holder.itemView?.context, DetailActivity::class.java)
                intent.putExtra("name",model.getProduct(position).name )
                intent.putExtra("price",model.getProduct(position).price )
                intent.putExtra("id",model.getProduct(position).id)
                ContextCompat.startActivity(holder.itemView.context,intent,null)
            }
        }
    }
}